import pytest
from unittest.mock import patch, MagicMock
from app.services import qr_service, email_service
from app.services.paystack import CircuitBreaker

def test_generate_qr_code():
    """Test QR code generation"""
    ticket_code = "TEST-123456"
    
    with patch('qrcode.QRCode') as mock_qr:
        mock_instance = MagicMock()
        mock_qr.return_value = mock_instance
        
        result = qr_service.generate_qr_code(ticket_code)
        
        assert ticket_code in result
        assert result.endswith('.png')
        mock_instance.add_data.assert_called_once_with(ticket_code)

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

@patch('smtplib.SMTP')
def test_send_email_success(mock_smtp):
    """Test successful email sending"""
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    result = email_service.send_ticket_email(
        to_email="test@example.com",
        user_name="Test User",
        event_title="Test Event",
        ticket_code="TEST-123",
        event_date="2024-12-31",
        event_location="Test Location"
    )
    
    assert result is True
    mock_server.starttls.assert_called_once()
    mock_server.send_message.assert_called_once()

@patch('smtplib.SMTP')
def test_send_email_failure(mock_smtp):
    """Test email sending failure handling"""
    mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")
    
    result = email_service.send_ticket_email(
        to_email="test@example.com",
        user_name="Test User",
        event_title="Test Event",
        ticket_code="TEST-123",
        event_date="2024-12-31",
        event_location="Test Location"
    )
    
    assert result is False