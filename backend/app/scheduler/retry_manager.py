import re

class RetryManager:
    """
    Manages job execution retries and delay policies.
    """
    
    @staticmethod
    def should_retry(error_message: str) -> bool:
        """
        Classifies errors to determine if a retry is warranted.
        Retries: Network errors, timeouts, rate-limits (429), server downtime (503).
        Skips: 404 Not Found, 403 Forbidden, and Validation Failures.
        """
        if not error_message:
            return False
            
        err = error_message.lower()
        
        # 1. Check for explicitly non-retryable status codes and messages
        non_retryable = [
            "403", "forbidden", "permission denied",
            "404", "not found",
            "validation failed", "validation_error", "validation error",
            "missing required field", "empty address",
            "missing", "empty", "validation"
        ]
        
        for phrase in non_retryable:
            if phrase in err:
                return False
                
        # 2. Check for retryable conditions
        retryable = [
            "timeout", "timed out", "connection", "network", 
            "ssl", "dns", "503", "service unavailable", 
            "429", "rate limit", "too many requests"
        ]
        
        for phrase in retryable:
            if phrase in err:
                return True
                
        # By default, if it's a generic unclassified error, we can attempt a retry
        return True

    @staticmethod
    def calculate_retry_delay(attempt: int, base_delay_minutes: int, policy: str = "EXPONENTIAL") -> int:
        """
        Calculates delay in seconds based on retry attempt, policy, and base delay.
        """
        base_seconds = base_delay_minutes * 60
        policy_upper = policy.upper() if policy else "EXPONENTIAL"
        
        if attempt <= 0:
            return 0
            
        if policy_upper == "IMMEDIATE":
            return 0
        elif policy_upper == "LINEAR":
            return attempt * base_seconds
        elif policy_upper == "EXPONENTIAL":
            return (2 ** (attempt - 1)) * base_seconds
        else:
            # Fallback to exponential
            return (2 ** (attempt - 1)) * base_seconds
