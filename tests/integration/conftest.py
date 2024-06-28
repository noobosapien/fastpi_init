from tests.utils.docker_utils import start_database_container
import pytest
import os
from sqlalchemy import create_engine
from tests.utils.databse_utils import migrate_to_db
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.db_connection import get_db_session


@pytest.fixture(scope="function")
def db_session_integration():
    container = start_database_container()

    engine = create_engine(os.getenv("TEST_DATABASE_URL"))

    with engine.begin() as connection:
        migrate_to_db("migrations", "alembic.ini", connection)

    SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    # yield SessionLocal
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

    container.stop()
    container.remove()
    engine.dispose()


@pytest.fixture()
def override_get_db_session(db_session_integration):
    def override():
        return db_session_integration

    app.dependency_overrides[get_db_session] = override


@pytest.fixture(scope="function")
def client(override_get_db_session):
    with TestClient(app) as _client:
        yield _client
