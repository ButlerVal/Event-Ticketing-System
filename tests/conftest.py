import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Sample user data"""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }

@pytest.fixture
def test_event_data():
    """Sample event data"""
    return {
        "title": "Test Event",
        "description": "A test event description",
        "event_date": "2024-12-31T20:00:00",
        "location": "Test Location",
        "price": 5000.00,
        "capacity": 100
    }

@pytest.fixture
def authenticated_user(client, test_user_data):
    """Create and authenticate a test user"""
    # Register user
    client.post("/auth/register", json=test_user_data)
    
    # Login
    response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = response.json()["access_token"]
    
    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_data": test_user_data
    }