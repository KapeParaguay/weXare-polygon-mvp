from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.services.auth import get_current_user
from app.core.config import settings

# Ensure all models are imported and registered
import app.models  # noqa: F401


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass

    def _get_user():
        return {"id": "user_1", "email": "user@example.com", "status": "ACTIVE", "roles": "CREATOR,WORKER,JUDGE"}

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_current_user] = _get_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
