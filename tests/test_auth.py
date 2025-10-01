import pytest
from fastapi import status

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"

def test_register_user_success(client, test_user_data):
    """Test successful user registration"""
    response = client.post("/auth/register", json=test_user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["name"] == test_user_data["name"]
    assert "password" not in data
    assert "password_hash" not in data

def test_register_duplicate_email(client, test_user_data):
    """Test registration with duplicate email fails"""
    # Register first time
    client.post("/auth/register", json=test_user_data)
    
    # Try to register again with same email
    response = client.post("/auth/register", json=test_user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()

def test_register_invalid_email(client, test_user_data):
    """Test registration with invalid email fails"""
    test_user_data["email"] = "invalid-email"
    response = client.post("/auth/register", json=test_user_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_short_password(client, test_user_data):
    """Test registration with short password fails"""
    test_user_data["password"] = "short"
    response = client.post("/auth/register", json=test_user_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_success(client, test_user_data):
    """Test successful login"""
    # Register user
    client.post("/auth/register", json=test_user_data)
    
    # Login
    response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user_data["email"]

def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password fails"""
    # Register user
    client.post("/auth/register", json=test_user_data)
    
    # Try login with wrong password
    response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": "wrongpassword"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_nonexistent_user(client):
    """Test login with non-existent user fails"""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "somepassword"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, authenticated_user):
    """Test getting current user info with valid token"""
    response = client.get("/auth/me", headers=authenticated_user["headers"])
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == authenticated_user["user_data"]["email"]

def test_get_current_user_no_token(client):
    """Test getting current user without token fails"""
    response = client.get("/auth/me")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token fails"""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED