"""
Unit tests for circuit breaker.
"""
import unittest
import time

from sentinel.circuit.breaker import (
    CircuitBreaker,
    CircuitBreakerRule,
    CircuitBreakerStrategy,
    CircuitBreakerState,
    CircuitBreakerManager,
)


class TestCircuitBreaker(unittest.TestCase):
    """Test cases for CircuitBreaker."""
    
    def test_circuit_opens_on_error_ratio(self):
        """Test circuit opens when error ratio exceeds threshold."""
        rule = CircuitBreakerRule(
            resource="test",
            strategy=CircuitBreakerStrategy.ERROR_RATIO,
            threshold=0.5,
            time_window_sec=10,
            recovery_timeout_ms=1000,
            min_request_amount=5
        )
        
        breaker = CircuitBreaker(rule)
        
        # Record 5 errors (100% error rate)
        for _ in range(5):
            breaker.record_error()
        
        # Circuit should be open
        self.assertFalse(breaker.can_pass())
        self.assertEqual(breaker.get_state(), CircuitBreakerState.OPEN)
    
    def test_circuit_closes_after_recovery(self):
        """Test circuit closes after recovery timeout."""
        rule = CircuitBreakerRule(
            resource="test",
            strategy=CircuitBreakerStrategy.ERROR_RATIO,
            threshold=0.5,
            time_window_sec=10,
            recovery_timeout_ms=100,  # Short timeout for testing
            min_request_amount=1
        )
        
        breaker = CircuitBreaker(rule)
        
        # Open circuit
        breaker.record_error()
        self.assertEqual(breaker.get_state(), CircuitBreakerState.OPEN)
        
        # Wait for recovery
        time.sleep(0.15)
        
        # Should allow test request (half-open)
        self.assertTrue(breaker.can_pass())
    
    def test_circuit_stays_closed_with_success(self):
        """Test circuit stays closed with successful requests."""
        rule = CircuitBreakerRule(
            resource="test",
            strategy=CircuitBreakerStrategy.ERROR_RATIO,
            threshold=0.5,
            time_window_sec=10,
            min_request_amount=10
        )
        
        breaker = CircuitBreaker(rule)
        
        # Record 5 successes
        for _ in range(5):
            breaker.record_success()
        
        # Circuit should still be closed
        self.assertEqual(breaker.get_state(), CircuitBreakerState.CLOSED)
        self.assertTrue(breaker.can_pass())
    
    def test_circuit_manager(self):
        """Test CircuitBreakerManager."""
        rule = CircuitBreakerRule(
            resource="test",
            strategy=CircuitBreakerStrategy.ERROR_COUNT,
            threshold=5,
            time_window_sec=10
        )
        
        CircuitBreakerManager.load_rules([rule])
        
        breaker = CircuitBreakerManager.get_breaker("test")
        self.assertIsNotNone(breaker)
        
        CircuitBreakerManager.clear_rules()


if __name__ == "__main__":
    unittest.main()
