import pytest
from fastapi import status
from unittest.mock import patch

@pytest.fixture
def created_ticket(client, authenticated_user, created_event, db_session):
    """Create a ticket for testing"""
    from app.cruds import tickets as ticket_crud
    
    ticket = ticket_crud.create_ticket(
        db=db_session,
        user_id=1,  # Assuming first user
        event_id=created_event["id"],
        amount=created_event["price"]
    )
    db_session.commit()
    return ticket

@pytest.fixture
def created_event(client, authenticated_user, test_event_data):
    """Create an event for testing"""
    response = client.post(
        "/events/",
        json=test_event_data,
        headers=authenticated_user["headers"]
    )
    return response.json()

def test_get_my_tickets_empty(client, authenticated_user):
    """Test getting tickets when user has none"""
    response = client.get(
        "/tickets/my-tickets",
        headers=authenticated_user["headers"]
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_get_my_tickets_with_data(
    client,
    authenticated_user,
    created_ticket
):
    """Test getting user's tickets"""
    response = client.get(
        "/tickets/my-tickets",
        headers=authenticated_user["headers"]
    )
    
    assert response.status_code == status.HTTP_200_OK
    tickets = response.json()
    assert len(tickets) >= 1
    assert tickets[0]["ticket_code"] == created_ticket.ticket_code

def test_get_my_tickets_no_auth(client):
    """Test getting tickets without authentication fails"""
    response = client.get("/tickets/my-tickets")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_ticket_by_code(client, created_ticket):
    """Test getting ticket by code (public endpoint)"""
    response = client.get(f"/tickets/{created_ticket.ticket_code}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["ticket_code"] == created_ticket.ticket_code

def test_get_ticket_invalid_code(client):
    """Test getting ticket with invalid code returns 404"""
    response = client.get("/tickets/INVALID-CODE")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND