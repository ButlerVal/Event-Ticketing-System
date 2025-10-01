import pytest
from fastapi import status

def test_list_events_empty(client):
    """Test listing events when database is empty"""
    response = client.get("/events/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_create_event_success(client, authenticated_user, test_event_data):
    """Test successful event creation"""
    response = client.post(
        "/events/",
        json=test_event_data,
        headers=authenticated_user["headers"]
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == test_event_data["title"]
    # FIX: Compare as float, not string
    assert float(data["price"]) == test_event_data["price"]
    assert data["capacity"] == test_event_data["capacity"]
    assert data["tickets_sold"] == 0

def test_create_event_no_auth(client, test_event_data):
    """Test creating event without authentication fails"""
    response = client.post("/events/", json=test_event_data)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_create_event_invalid_data(client, authenticated_user):
    """Test creating event with invalid data fails"""
    invalid_data = {
        "title": "AB",  # Too short
        "description": "Test",
        "event_date": "invalid-date",
        "location": "Test",
        "price": -100,  # Negative price
        "capacity": 0  # Zero capacity
    }
    
    response = client.post(
        "/events/",
        json=invalid_data,
        headers=authenticated_user["headers"]
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_list_events_with_data(client, authenticated_user, test_event_data):
    """Test listing events returns created events"""
    client.post(
        "/events/",
        json=test_event_data,
        headers=authenticated_user["headers"]
    )
    
    response = client.get("/events/")
    
    assert response.status_code == status.HTTP_200_OK
    events = response.json()
    assert len(events) == 1
    assert events[0]["title"] == test_event_data["title"]

def test_get_event_by_id(client, authenticated_user, test_event_data):
    """Test getting specific event by ID"""
    create_response = client.post(
        "/events/",
        json=test_event_data,
        headers=authenticated_user["headers"]
    )
    event_id = create_response.json()["id"]
    
    response = client.get(f"/events/{event_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == event_id
    assert data["title"] == test_event_data["title"]

def test_get_nonexistent_event(client):
    """Test getting non-existent event returns 404"""
    response = client.get("/events/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_events_pagination(client, authenticated_user, test_event_data):
    """Test event listing pagination"""
    for i in range(5):
        event_data = test_event_data.copy()
        event_data["title"] = f"Event {i}"
        client.post(
            "/events/",
            json=event_data,
            headers=authenticated_user["headers"]
        )
    
    response = client.get("/events/?skip=0&limit=3")
    assert len(response.json()) == 3
    
    response = client.get("/events/?skip=3&limit=3")
    assert len(response.json()) == 2