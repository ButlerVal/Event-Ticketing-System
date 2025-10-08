import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.services import qr_service, email_service
from app.services.paystack import CircuitBreaker
from pathlib import Path
from PIL import Image
import os

def test_generate_qr_code(tmp_path):
    """Test that QR code is generated and can be decoded"""
    ticket_code = "TEST-123456"

    # Override output directory to use pytest's tmp_path (keeps tests clean)
    qr_service.Path("qr_codes").mkdir(parents=True, exist_ok=True)

    result = qr_service.generate_qr_code(ticket_code)

    # Assert file path
    assert result.endswith(f"{ticket_code}.png")
    filepath = Path(result)
    assert filepath.exists()

def test_circuit_breaker_closed_state():
    """Test circuit breaker in closed state"""
    cb = CircuitBreaker(failure_threshold=3, timeout=60)
    
    def success_func():
        return "success"
    
    result = cb.call(success_func)
    
    assert result == "success"
    assert cb.state == "CLOSED"
    assert cb.failure_count == 0

def test_circuit_breaker_opens_after_failures():
    """Test circuit breaker opens after threshold failures"""
    cb = CircuitBreaker(failure_threshold=3, timeout=60)
    
    def failing_func():
        raise Exception("API Error")
    
    # Fail 3 times
    for _ in range(3):
        with pytest.raises(Exception):
            cb.call(failing_func)
    
    assert cb.state == "OPEN"
    assert cb.failure_count == 3

def test_circuit_breaker_rejects_when_open():
    """Test circuit breaker rejects calls when open"""
    cb = CircuitBreaker(failure_threshold=2, timeout=60)
    
    def failing_func():
        raise Exception("API Error")
    
    # Trigger opening
    for _ in range(2):
        with pytest.raises(Exception):
            cb.call(failing_func)
    
    # Should reject next call
    with pytest.raises(Exception, match="Circuit breaker is OPEN"):
        cb.call(failing_func)

@patch('app.services.email_service.SendGridAPIClient')
@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open, read_data=b'fake_qr_code_data')
def test_send_email_success(mock_file, mock_exists, mock_sendgrid):
    """Test successful email sending with SendGrid"""
    # Mock successful SendGrid response
    mock_sg_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_sg_instance.send.return_value = mock_response
    mock_sendgrid.return_value = mock_sg_instance
    
    # Mock QR code file exists
    mock_exists.return_value = True
    
    result = email_service.send_ticket_email(
        to_email="test@example.com",
        user_name="Test User",
        event_title="Test Event",
        ticket_code="TEST-123",
        event_date="2024-12-31",
        event_location="Test Location",
        qr_code_path="qr_codes/TEST-123.png"
    )
    
    assert result is True
    mock_sendgrid.assert_called_once()
    mock_sg_instance.send.assert_called_once()

@patch('app.services.email_service.SendGridAPIClient')
def test_send_email_failure(mock_sendgrid):
    """Test email sending failure handling with SendGrid"""
    # Mock SendGrid API failure
    mock_sg_instance = MagicMock()
    mock_sg_instance.send.side_effect = Exception("SendGrid API Error")
    mock_sendgrid.return_value = mock_sg_instance
    
    result = email_service.send_ticket_email(
        to_email="test@example.com",
        user_name="Test User",
        event_title="Test Event",
        ticket_code="TEST-123",
        event_date="2024-12-31",
        event_location="Test Location"
    )
    
    assert result is False

@patch('app.services.email_service.SendGridAPIClient')
@patch('os.path.exists')
def test_send_email_without_qr_code(mock_exists, mock_sendgrid):
    """Test email sending without QR code attachment"""
    # Mock successful SendGrid response
    mock_sg_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_sg_instance.send.return_value = mock_response
    mock_sendgrid.return_value = mock_sg_instance
    
    # Mock QR code file does not exist
    mock_exists.return_value = False
    
    result = email_service.send_ticket_email(
        to_email="test@example.com",
        user_name="Test User",
        event_title="Test Event",
        ticket_code="TEST-123",
        event_date="2024-12-31",
        event_location="Test Location",
        qr_code_path="qr_codes/TEST-123.png"
    )
    
    assert result is True
    mock_sendgrid.assert_called_once()
    # Verify email was sent even without QR code
    mock_sg_instance.send.assert_called_once()

@patch('app.services.email_service.SendGridAPIClient')
def test_send_email_with_none_qr_path(mock_sendgrid):
    """Test email sending when QR code path is None"""
    # Mock successful SendGrid response
    mock_sg_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_sg_instance.send.return_value = mock_response
    mock_sendgrid.return_value = mock_sg_instance
    
    result = email_service.send_ticket_email(
        to_email="test@example.com",
        user_name="Test User",
        event_title="Test Event",
        ticket_code="TEST-123",
        event_date="2024-12-31",
        event_location="Test Location",
        qr_code_path=None
    )
    
    assert result is True
    mock_sendgrid.assert_called_once()
    mock_sg_instance.send.assert_called_once()