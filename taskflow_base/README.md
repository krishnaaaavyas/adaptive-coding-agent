# TaskFlow

TaskFlow is a small FastAPI application for managing projects and tasks.
It uses SQLAlchemy with an in-memory SQLite database and Pydantic models
for request and response data.

## Setup

```
pip install -r requirements.txt
python -m pytest -q
```

## Run the application

```
uvicorn main:app --reload
```

The API provides endpoints for creating projects and creating tasks within
projects. Interactive API documentation is available at `/docs` while the
application is running.

## Project structure

- `routers/` defines the HTTP endpoints.
- `services/` contains application logic.
- `repositories/` handles persistence.
- `models/` contains SQLAlchemy models.
- `dto/` contains request and response models.
- `core/` provides shared database, result, error, and logging utilities.
