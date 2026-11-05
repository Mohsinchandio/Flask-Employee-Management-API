import tempfile
import unittest
from app import create_app


class EmployeeAPITestCase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.app = create_app({
            "TESTING": True,
            "DATABASE": self.temp_db.name,
            "JWT_SECRET_KEY": "test-secret-key",
        })
        self.client = self.app.test_client()

    def tearDown(self):
        import os
        os.unlink(self.temp_db.name)

    def login(self, username, password):
        response = self.client.post(
            "/api/login",
            json={"username": username, "password": password},
        )
        return response.get_json()["access_token"]

    def test_unauthenticated_cannot_view(self):
        response = self.client.get("/api/employees")
        self.assertEqual(response.status_code, 401)

    def test_employee_can_view_but_cannot_add(self):
        token = self.login("employee", "Employee@123")
        headers = {"Authorization": f"Bearer {token}"}
        self.assertEqual(self.client.get("/api/employees", headers=headers).status_code, 200)
        response = self.client.post(
            "/api/employees",
            headers=headers,
            json={"name": "Test User", "email": "test@example.com",
                  "department": "IT", "position": "Tester"},
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_add_employee(self):
        token = self.login("admin", "Admin@123")
        response = self.client.post(
            "/api/employees",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Test User", "email": "test@example.com",
                  "department": "IT", "position": "Tester"},
        )
        self.assertEqual(response.status_code, 201)

    def test_invalid_login(self):
        response = self.client.post(
            "/api/login", json={"username": "admin", "password": "bad"}
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
