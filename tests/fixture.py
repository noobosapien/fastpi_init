from .utils.docker_utils import start_database_container
import pytest
import os
from sqlalchemy import create_engine
from tests.utils.databse_utils import migrate_to_db
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session", autouse=True)
def db_session():
    container = start_database_container()

    engine = create_engine(os.getenv("TEST_DATABASE_URL"))

    with engine.begin() as connection:
        migrate_to_db("migrations", "alembic.ini", connection)

    SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    yield SessionLocal

    container.stop()
    container.remove()
    engine.dispose()
