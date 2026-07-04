import pytest
from app.scheduler.retry_manager import RetryManager

def test_retry_classification():
    # Retryable cases
    assert RetryManager.should_retry("Connection timed out after 30s") is True
    assert RetryManager.should_retry("HTTP 503 Service Unavailable") is True
    assert RetryManager.should_retry("HTTP 429 Too Many Requests") is True
    assert RetryManager.should_retry("Network error: Name or service not known") is True
    
    # Non-retryable cases
    assert RetryManager.should_retry("HTTP 404 Not Found") is False
    assert RetryManager.should_retry("HTTP 403 Forbidden") is False
    assert RetryManager.should_retry("Validation failed: Pincode is missing") is False
    assert RetryManager.should_retry("Dealer name is missing or empty") is False

def test_retry_delay_calculations():
    # Base delay = 5 minutes
    
    # Immediate
    assert RetryManager.calculate_retry_delay(1, 5, "IMMEDIATE") == 0
    
    # Linear: attempt * base (1st = 5min, 2nd = 10min)
    assert RetryManager.calculate_retry_delay(1, 5, "LINEAR") == 5 * 60
    assert RetryManager.calculate_retry_delay(2, 5, "LINEAR") == 10 * 60
    
    # Exponential: 2^(attempt-1) * base (1st = 5min, 2nd = 10min, 3rd = 20min)
    assert RetryManager.calculate_retry_delay(1, 5, "EXPONENTIAL") == 5 * 60
    assert RetryManager.calculate_retry_delay(2, 5, "EXPONENTIAL") == 10 * 60
    assert RetryManager.calculate_retry_delay(3, 5, "EXPONENTIAL") == 20 * 60
