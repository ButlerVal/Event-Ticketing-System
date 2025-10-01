import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

@pytest.fixture
def mock_paystack_initialize():
    """Mock successful Paystack initialization"""
    with patch('app.services.paystack.initialize_payment') as mock:
        mock.return_value = {
            'status': True,
            'data': {
                'authorization_url': 'https://checkout.paystack.com/test',
                'access_code': 'test_access_code',
                'reference': 'test_reference'
            }
        }
        yield mock

@pytest.fixture
def mock_paystack_verify():
    """Mock successful Paystack verification"""
    with patch('app.services.paystack.verify_payment') as mock:
        mock.return_value = {
            'status': True,
            'data': {
                'status': 'success',
                'reference': 'test_reference',
                'amount': 500000
            }
        }
        yield mock

@pytest.fixture
def created_event(client, authenticated_user, test_event_data):
    """Create an event for testing"""
    response = client.post(
        "/events/",
        json=test_event_data,
        headers=authenticated_user["headers"]
    )
    return response.json()

def test_initialize_payment_success(
    client,
    authenticated_user,
    created_event,
    mock_paystack_initialize
):
    """Test successful payment initialization"""
    payment_data = {
        "event_id": created_event["id"],
        "email": authenticated_user["user_data"]["email"]
    }
    
    response = client.post(
        "/payments/initialize",
        json=payment_data,
        headers=authenticated_user["headers"]
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "authorization_url" in data
    assert "reference" in data
    assert "access_code" in data

def test_initialize_payment_no_auth(client, created_event):
    """Test payment initialization without authentication fails"""
    payment_data = {
        "event_id": created_event["id"],
        "email": "test@example.com"
    }
    
    response = client.post("/payments/initialize", json=payment_data)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_initialize_payment_invalid_event(
    client,
    authenticated_user,
    mock_paystack_initialize
):
    """Test payment initialization with invalid event fails"""
    payment_data = {
        "event_id": 99999,
        "email": authenticated_user["user_data"]["email"]
    }
    
    response = client.post(
        "/payments/initialize",
        json=payment_data,
        headers=authenticated_user["headers"]
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

@patch('app.services.email_service.send_ticket_email')
@patch('app.services.qr_service.generate_qr_code')
def test_verify_payment_success(
    mock_qr,
    mock_email,
    client,
    authenticated_user,
    created_event,
    mock_paystack_initialize,
    mock_paystack_verify
):
    """Test successful payment verification"""
    # Mock QR code generation
    mock_qr.return_value = "qr_codes/test.png"
    mock_email.return_value = True
    
    # Initialize payment
    payment_data = {
        "event_id": created_event["id"],
        "email": authenticated_user["user_data"]["email"]
    }
    init_response = client.post(
        "/payments/initialize",
        json=payment_data,
        headers=authenticated_user["headers"]
    )
    reference = init_response.json()["reference"]
    
    # Verify payment
    response = client.get(
        f"/payments/verify/{reference}",
        headers=authenticated_user["headers"]
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "ticket_code" in data
    assert data["message"] == "Payment verified successfully"

def test_verify_payment_invalid_reference(client, authenticated_user):
    """Test verifying payment with invalid reference fails"""
    response = client.get(
        "/payments/verify/invalid_reference",
        headers=authenticated_user["headers"]
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND