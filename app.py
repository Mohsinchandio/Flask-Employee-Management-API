import os
import sqlite3
from functools import wraps

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt, get_jwt_identity,
    jwt_required
)
from werkzeug.security import generate_password_hash, check_password_hash


def get_db_connection():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('employee', 'administrator'))
        );

        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            position TEXT NOT NULL
        );
    """)
    # Demo accounts are created only when the database is first initialized.
    demo_users = [
        ("admin", generate_password_hash("Admin@123"), "administrator"),
        ("employee", generate_password_hash("Employee@123"), "employee"),
    ]
    for username, password_hash, role in demo_users:
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )

    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO employees (name, email, department, position) VALUES (?, ?, ?, ?)",
            [
                ("Ali Khan", "ali@example.com", "IT", "Developer"),
                ("Sara Ahmed", "sara@example.com", "HR", "HR Officer"),
            ],
        )
    conn.commit()
    conn.close()


def admin_required(fn):
    """Allow only authenticated users whose JWT role is administrator."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if get_jwt().get("role") != "administrator":
            return jsonify(error="Forbidden", message="Administrator role required"), 403
        return fn(*args, **kwargs)
    return wrapper


def create_app(test_config=None):
    application = Flask(__name__)
    application.config.update(
        JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "development-only-change-this-secret"),
        JWT_ACCESS_TOKEN_EXPIRES=False,
        DATABASE=os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "employees.db")),
    )
    if test_config:
        application.config.update(test_config)

    JWTManager(application)

    # Routes close over this app's database configuration.
    global app
    app = application
    with application.app_context():
        init_db()

    @application.get("/")
    def home():
        return jsonify(
            message="Employee Management API",
            endpoints={
                "login": "POST /api/login",
                "list_employees": "GET /api/employees",
                "add_employee": "POST /api/employees (administrator)",
                "update_employee": "PUT /api/employees/<id> (administrator)",
                "delete_employee": "DELETE /api/employees/<id> (administrator)",
            },
        )

    @application.post("/api/login")
    def login():
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify(error="username and password are required"), 400

        conn = get_db_connection()
        user = conn.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            return jsonify(error="Invalid username or password"), 401

        token = create_access_token(
            identity=str(user["id"]),
            additional_claims={"role": user["role"], "username": user["username"]},
        )
        return jsonify(
            message="Login successful",
            access_token=token,
            token_type="Bearer",
            role=user["role"],
        ), 200

    @application.get("/api/employees")
    @jwt_required()
    def list_employees():
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT id, name, email, department, position FROM employees ORDER BY id"
        ).fetchall()
        conn.close()
        return jsonify(employees=[dict(row) for row in rows]), 200

    @application.post("/api/employees")
    @admin_required
    def add_employee():
        data = request.get_json(silent=True) or {}
        required = ("name", "email", "department", "position")
        missing = [field for field in required if not isinstance(data.get(field), str) or not data[field].strip()]
        if missing:
            return jsonify(error="Missing or empty required fields", fields=missing), 400

        conn = get_db_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO employees (name, email, department, position) VALUES (?, ?, ?, ?)",
                tuple(data[field].strip() for field in required),
            )
            conn.commit()
            employee_id = cursor.lastrowid
            row = conn.execute(
                "SELECT id, name, email, department, position FROM employees WHERE id = ?",
                (employee_id,),
            ).fetchone()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify(error="An employee with this email already exists"), 409
        conn.close()
        return jsonify(message="Employee created", employee=dict(row)), 201

    @application.put("/api/employees/<int:employee_id>")
    @admin_required
    def update_employee(employee_id):
        data = request.get_json(silent=True) or {}
        allowed = ("name", "email", "department", "position")
        if not data or any(key not in allowed for key in data):
            return jsonify(error="Provide one or more valid employee fields"), 400
        if any(not isinstance(value, str) or not value.strip() for value in data.values()):
            return jsonify(error="Employee fields must be non-empty strings"), 400

        conn = get_db_connection()
        existing = conn.execute("SELECT id FROM employees WHERE id = ?", (employee_id,)).fetchone()
        if existing is None:
            conn.close()
            return jsonify(error="Employee not found"), 404

        assignments = ", ".join(f"{key} = ?" for key in data)
        values = [value.strip() for value in data.values()] + [employee_id]
        try:
            conn.execute(f"UPDATE employees SET {assignments} WHERE id = ?", values)
            conn.commit()
            row = conn.execute(
                "SELECT id, name, email, department, position FROM employees WHERE id = ?",
                (employee_id,),
            ).fetchone()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify(error="An employee with this email already exists"), 409
        conn.close()
        return jsonify(message="Employee updated", employee=dict(row)), 200

    @application.delete("/api/employees/<int:employee_id>")
    @admin_required
    def delete_employee(employee_id):
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        conn.commit()
        conn.close()
        if cursor.rowcount == 0:
            return jsonify(error="Employee not found"), 404
        return jsonify(message="Employee deleted"), 200

    return application


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=True)
