# Winterfell

Winterfell is a full-stack event management application built with **Python**, **FastAPI**, **SQLModel**, **SQLite**, **React**, and **Vite**.

The project provides an API for managing users, events, tickets, event staff, attendee registration, authentication, and check-in operations.

**Status:** Work in Progress (WIP)

---

## Features

### Authentication

* JWT-based authentication
* User login
* Protected API routes
* Role-based permissions

### User Management

* User creation
* User lookup
* User deletion
* Authenticated user information

### Event Management

* Create events
* List events
* Get event details
* Delete events
* Add staff members to events
* Event-specific roles and permissions

### Ticket Management

* Create attendee tickets
* Ticket-based event access
* Ticket cancellation
* Ticket status management

### Check-in System

* Ticket check-in
* Check-in validation
* Check-in timestamps
* Check-in history and logs
* Staff and administrator permissions

### Other Features

* SQLite database persistence
* Automatic API documentation with FastAPI
* Automated testing with Pytest
* Environment variable support
* React frontend integration

---

## Tech Stack

### Backend

* Python 3.13
* FastAPI
* SQLModel
* SQLite
* PyJWT
* Uvicorn
* Pytest
* pytest-cov
* uv

### Frontend

* React
* Vite
* JavaScript

---

## Project Structure

```text
Winterfell/
│
├── backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │   ├── attendees/
│   │   ├── core/
│   │   ├── events/
│   │   ├── users/
│   │   ├── database.sqlite
│   │   └── ...
│   │
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── .env
│   └── .venv/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
└── README.md
```

### Main directories

* `backend/app/` → FastAPI application source code
* `frontend/` → React frontend application
* `database.sqlite` → Local development database

---

## Prerequisites

Before running the project, make sure you have installed:

* Python 3.11 or newer
* Node.js
* npm
* Git

The project uses **uv** for Python dependency management.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Winterfell
```

---

### 2. Backend setup

Move into the backend directory:

```bash
cd backend
```

Install the Python dependencies using `uv`:

```bash
uv sync
```

The virtual environment is automatically managed by `uv`.

If necessary, activate the virtual environment manually.

#### Linux / macOS

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

---

## Environment Variables

Create a `.env` file inside the `backend` directory:

```env
SECRET_KEY=your_secret_key_here
```

You can generate a secure secret key using:

```bash
openssl rand -hex 32
```

### Environment variables

| Variable     | Description                                         |
| ------------ | --------------------------------------------------- |
| `SECRET_KEY` | Secret key used to generate and validate JWT tokens |

> Never commit your `.env` file or secret keys to the repository.

---

## Running the Backend

From the `backend` directory, run:

```bash
uvicorn app.main:app --reload
```

The `--reload` option automatically restarts the server whenever changes are detected.

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## Frontend Setup

Open a new terminal and move into the frontend directory:

```bash
cd Winterfell/frontend
```

Install the frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will usually be available at:

```text
http://localhost:5173
```

---

## API Documentation

FastAPI automatically generates interactive API documentation.

After starting the backend, open:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

## Running Tests

From the `backend` directory, run all tests:

```bash
pytest
```

Run tests in verbose mode:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/<test_file>.py
```

Run tests with coverage:

```bash
pytest --cov
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

---

## Available Endpoints

### Miscellaneous

| Method | Endpoint    | Description               |
| ------ | ----------- | ------------------------- |
| `GET`  | `/`         | API welcome message       |
| `GET`  | `/db-check` | Check database connection |

---

### Authentication

| Method | Endpoint | Description                              |
| ------ | -------- | ---------------------------------------- |
| `POST` | `/login` | Authenticate a user                      |
| `GET`  | `/me`    | Get the authenticated user's information |

---

### Users

| Method   | Endpoint                  | Description          |
| -------- | ------------------------- | -------------------- |
| `POST`   | `/users`                  | Create a user        |
| `GET`    | `/users/by-email/{email}` | Find a user by email |
| `GET`    | `/users/{user_id}`        | Get a user           |
| `DELETE` | `/users/{user_id}`        | Delete a user        |

---

### Attendees

| Method   | Endpoint                             | Description               |
| -------- | ------------------------------------ | ------------------------- |
| `GET`    | `/attendees/organizers/{event_id}`   | List event organizers     |
| `GET`    | `/attendees/participants/{event_id}` | List event participants   |
| `GET`    | `/attendees/{attendee_id}`           | Get attendee information  |
| `DELETE` | `/attendees/{id}`                    | Delete an attendee        |
| `POST`   | `/attendees/tickets`                 | Create an attendee ticket |

---

### Events

| Method   | Endpoint                                | Description             |
| -------- | --------------------------------------- | ----------------------- |
| `GET`    | `/events/`                              | List events             |
| `POST`   | `/events/`                              | Create an event         |
| `GET`    | `/events/{event_id}`                    | Get event details       |
| `DELETE` | `/events/{event_id}`                    | Delete an event         |
| `POST`   | `/events/{event_id}/addstaff/{user_id}` | Add staff to an event   |
| `POST`   | `/events/{ticket_code}/check-in`        | Check in a ticket       |
| `GET`    | `/events/{event_id}/check-in-logs`      | Get event check-in logs |

---

## Roles and Permissions

The application supports event-specific user roles.

Current roles include:

* `attendee`
* `user`
* `staff`
* `admin`

Permissions are managed according to the user's role within a specific event.

---

## Current Development Goals

* Cloud deployment
* Better API structure and modularization
* Improved validation and exception handling
* CI/CD pipeline implementation
* Performance optimization
* Additional automated test coverage

---

## Contributing

This project is currently under active development.

Suggestions, improvements, and contributions are welcome.

---

## Project Status

**Work in Progress**

Winterfell is an ongoing learning project focused on:

* Backend engineering
* REST API development
* Authentication systems
* Database management
* Role-based access control
* Event management systems
* Full-stack application development
* Automated testing

---

## License

This project currently does not have a defined license.
