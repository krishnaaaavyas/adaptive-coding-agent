from fastapi import FastAPI

from core.db import Base, engine
from routers import projects, tasks

# Import model modules before create_all so their tables are registered
# on Base.metadata.
from models import project, task  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow")
app.include_router(tasks.router)
app.include_router(projects.router)
