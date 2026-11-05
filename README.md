Flask Employee Management API

"Python" (https://img.shields.io/badge/Python-3.9+-blue)
"Flask" (https://img.shields.io/badge/Flask-REST%20API-black)
"Database" (https://img.shields.io/badge/Database-SQLite-green)
"Authentication" (https://img.shields.io/badge/Auth-JWT-orange)

Project Overview

The Flask Employee Management API is a RESTful web service developed using Python and Flask. It implements JWT-based Authentication and Role-Based Authorization to securely manage employee records.

The system supports two user roles: Employee and Administrator. Employees can view employee records, while Administrators have full access to add, view, update, and delete employee records.

Features

- User Authentication using JWT
- Role-Based Authorization
- Secure Password Hashing
- Employee Record Management
- Add New Employees
- View Employee Records
- Update Employee Information
- Delete Employee Records
- SQLite Database Integration
- API Testing using cURL

Technologies Used

- Python
- Flask
- Flask-JWT-Extended
- SQLite
- REST API
- cURL

User Roles and Permissions

Operation| Employee| Administrator
Login| Yes| Yes
View Employees| Yes| Yes
Add Employees| No| Yes
Update Employees| No| Yes
Delete Employees| No| Yes

Demo Login Credentials

Role| Username| Password
Administrator| admin| Admin@123
Employee| employee| Employee@123

Note: These credentials are for local testing only.

Project Structure

Flask-Employee-Management-API/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
└── test_api.py

Installation and Setup

1. Clone Repository

git clone YOUR_GITHUB_REPOSITORY_URL

2. Open Project Folder

cd Flask-Employee-Management-API

3. Create Virtual Environment

python -m venv .venv

4. Activate Virtual Environment

Windows:

.venv\Scripts\activate

5. Install Dependencies

pip install -r requirements.txt

6. Run Flask Application

python app.py

The API will run at:

http://127.0.0.1:5000

API Endpoints

Method| Endpoint| Description| Access
POST| /api/login| User login| Public
GET| /api/employees| View employees| Employee/Admin
POST| /api/employees| Add employee| Admin
PUT| /api/employees/id| Update employee| Admin
DELETE| /api/employees/id| Delete employee| Admin

Authentication and Authorization

The API uses JSON Web Tokens (JWT) to authenticate users.

After successful login, the server generates an access token. Users must include this token in the Authorization header when accessing protected endpoints.

Example:

Authorization: Bearer YOUR_ACCESS_TOKEN

HTTP Status Codes

Status Code| Meaning
200| Request successful
201| Employee created
400| Invalid request
401| Unauthorized / Authentication required
403| Forbidden / Insufficient permissions
404| Employee not found
409| Duplicate employee email

Testing

The API can be tested using:

- cURL
- Postman
- Python unittest

Run automated tests:

python -m unittest test_api.py

Authentication vs Authorization

Authentication: Verifies the identity of a user through valid login credentials.

Authorization: Determines which operations an authenticated user is permitted to perform according to their role.

For example:

- An unauthenticated user receives HTTP 401.
- An authenticated Employee attempting to add an employee receives HTTP 403.
- An Administrator can perform all employee management operations.

Project Purpose

This project was developed as a university assignment to demonstrate Authentication and Authorization concepts in a Flask REST API.

Author

Mohsin
