# Winterfell

Winterfell is a backend-focused web application built with Python using the FastAPI framework. The goal of this project is to provide a small and extensible REST API architecture with authentication, database persistence, and automated testing.

The project currently uses SQLModel with SQLite for local development and is actively being expanded with frontend integration.

**Status:** Work in Progress (WIP)

---

# Features

Currently implemented:

* JWT-based authentication system
* Customer CRUD operations
* Order CRUD operations
* SQLite database persistence
* Automated testing with Pytest
* Environment variable support using `.env`
* API documentation generated automatically by FastAPI

Planned features:

* Frontend integration using React
* Cloud deployment
* Better project modularization
* Improved validation and exception handling

---

# Tech Stack

Backend technologies currently used:

* Python 3.13
* FastAPI
* SQLModel
* SQLite
* JWT Authentication
* Pytest
* Uvicorn
* uv

Frontend (in development):

* React

---

# Prerequisites

Before running the project, make sure you have installed:

* Python 3.11 or newer (recommended)
* Git

Optional but recommended:

* uv for dependency management

---

# Project Structure

```bash
Winterfell/
│
├── backend/
│   ├── main.py
│   ├── tests/
│   ├── database.sqlite
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── .env
│   └── .venv
│
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
└── README.md
```

* `backend/` → API source code and tests
* `frontend/` → Frontend application (currently under development)

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd Winterfell
```

Move into the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

Linux / macOS

```bash
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

---

# Installing Dependencies

This project uses uv.

Install dependencies with:

```bash
uv sync
```

If you prefer pip:

```bash
pip install "fastapi[standard]" sqlmodel uvicorn pytest python-dotenv pyjwt
```

---

# Environment Variables

Create a `.env` file inside the `backend` folder.

Example:

```env
SECRET_KEY=your_secret_key_here
```

You can generate a secure secret key using:

```bash
openssl rand -hex 32
```

Environment variables currently used:

| Variable   | Description                              |
| ---------- | ---------------------------------------- |
| SECRET_KEY | Secret key used for JWT token generation |

---

# Database

The project uses SQLite for local development.

Main database:

```bash
backend/database.sqlite
```

Test database:

```bash
backend/test_database.sqlite
```

The database is automatically created when running the application.

---

# Running the Application

Inside the backend directory:

```bash
cd backend
```

Development mode:

```bash
uv run fastapi dev main.py
```

This mode automatically reloads the API whenever code changes are detected.

Production mode:

```bash
uv run fastapi run main.py
```

This mode is optimized for performance and does not automatically reload code changes.

---

# Frontend Setup

Move into the frontend directory:

```bash
cd ../frontend
```

Install frontend dependencies:

```bash
npm install
```

---

# Running Frontend

Inside the frontend folder:

```bash
cd frontend
```

Start development server:

```bash
npm run dev
```

The frontend application will be available locally through the Vite development server.

Example:

```bash
http://localhost:5173
```

# API Documentation

FastAPI automatically generates interactive API documentation.

After running the server, open:

```bash
http://127.0.0.1:8000/docs
```

Interactive Swagger documentation:

* `/docs` → Swagger UI
* `/redoc` → ReDoc documentation

---

# Running Tests

The project uses Pytest for automated testing.

Run all tests:

```bash
cd backend
pytest
```

Run a specific test file:

```bash
pytest tests/test_order.py
```

Verbose mode:

```bash
pytest -v
```

---

# Authentication

The API uses JWT-based authentication.

Protected routes require a valid Bearer Token.

Example header:

```http
Authorization: Bearer <token>
```

Authentication flow:

1. Create user account
2. Login
3. Receive JWT token
4. Use token in protected routes

---

# Available Endpoints

### Authentication

* POST `/login`

---

### Customers

* POST `/customers`
* GET `/customers`
* GET `/customers/{id}`
* PUT `/customers/{id}`
* DELETE `/customers/{id}`

---

### Orders

* POST `/orders`
* GET `/orders`
* GET `/orders/{id}`
* PUT `/orders/{id}`
* DELETE `/orders/{id}`

---

# Current Development Goals

Current priorities for development:

* Frontend integration with React
* Better API structure and modularization
* Deployment to cloud environment
* CI/CD pipeline implementation
* Performance optimization
* Additional automated test coverage

---

# Contributing

This project is currently under active development.

Contributions, suggestions, and improvements are welcome.

---

# Project Status

Current status:

**Work in Progress**

This project is being actively developed as a learning project focused on backend engineering, API design, authentication systems, database management, and full stack integration.

---

# License

This project currently does not have a defined license.
