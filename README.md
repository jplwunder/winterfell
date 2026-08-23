# Winterfell

Winterfell is an event management application built with **Python**, **FastAPI**, **SQLModel**, **SQLite**.

The project provides an API for managing users, events, tickets, event staff, attendee registration, authentication, and check-in operations.

**Status:** Work in Progress (WIP)

---

## Setup

Install `uv`:

* MacOs / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
* Windows
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Install the Python dependencies using `uv`:

```bash
uv sync
```

The virtual environment is automatically managed by `uv`.

### Environment Variables

Create a `.env` file

```bash
touch .env
```

Set these variables in your .env file
```env
SECRET_KEY=your_secret_key_here
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
MAIL_FROM = ""
MAIL_PORT = "587"
MAIL_SERVER = ""
MAIL_FROM_NAME=""
DOMAIN = ""
```

You can generate a secure secret key using:

```bash
openssl rand -hex 32
```

### Run the Application

```bash
uv run uvicorn app.main:app --reload
```

The `--reload` option automatically restarts the server whenever changes are detected.

The API will be available at:

```text
http://127.0.0.1:8000
```

---


## API Documentation

FastAPI automatically generates interactive API documentation.

After starting the backend, open:

```text
http://127.0.0.1:8000/docs
```

## Running Tests

From the `backend` directory, run all tests:

```bash
uv run pytest
```

Run tests in verbose mode:

```bash
uv run pytest -v
```

Run a specific test file:

```bash
uv run pytest tests/<test_file>.py
```

Run tests with coverage:

```bash
uv run pytest --cov
```

---

## Authentication

The API uses JWT-based authentication.

Protected routes require a valid Bearer Token.

Example:

```http
Authorization: Bearer <token>
```

### Authentication flow

1. Create a user account
2. Log in
3. Receive a JWT token
4. Include the token in protected API requests
