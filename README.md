# Winterfell

Winterfell is a Python backend project built with FastAPI. The goal of this repository is to provide a small, extensible API that uses `SQLModel` with SQLite for local development (project is in active development).

Status: WIP (work in progress)

## Prerequisites

- Python 3.11 or newer (recommended)
- Git

## Repository layout

- `winterfell/` — application package (contains `main.py` and source code)
- `pyproject.toml` — project metadata and dependencies
- `README.md` — this file

> Note: the current application entry point is `winterfell/main.py`.

## Quick start (development)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install runtime dependencies (quick):

```bash
pip install "fastapi[standard]" sqlmodel uvicorn
```


## Running the application

From the directory that contains `main.py` (or from the repository root using `--app-dir`), run:

```bash
# this will run the app in development mode, tailored so quick changes in code automatically refresh the API and load the updates

uv run fastapi dev main.py
```

For non-development purposes, run:

```bash
# this will run the app in production mode, tailored for faster response time, but does'nt refresh the changes automatically

uv run fastapi run main.py
```

Open `http://127.0.0.1:8000/docs` to view the interactive API docs provided by FastAPI.


