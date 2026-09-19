import pytest

from core.db import Base, engine


@pytest.fixture(autouse=True)
def reset_database():
    """The in-memory sqlite DB (StaticPool) persists for the whole process,
    so without this, tests would leak state into each other and IDs like
    project_id=1 would only be correct on the very first test that runs."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
