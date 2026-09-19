from fastapi import FastAPI

from core.db import Base, engine
from routers import projects, tasks

# Import every model module before create_all so its table is registered
# on Base.metadata. comments.py does not exist yet on purpose.
from models import project, task  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow")
app.include_router(tasks.router)
app.include_router(projects.router)
