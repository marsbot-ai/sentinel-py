"""
Example: Circuit Breaker with Sentinel

Demonstrates circuit breaker functionality.
"""
import time
import random
from sentinel import Sentinel
from sentinel.circuit import CircuitBreakerRule, CircuitBreakerStrategy


def test_error_ratio_breaker():
    """Test error ratio based circuit breaker."""
    print("=== Error Ratio Circuit Breaker ===")
    
    # Open circuit when error ratio > 50%
    rule = CircuitBreakerRule(
        resource="unstable_api",
        strategy=CircuitBreakerStrategy.ERROR_RATIO,
        threshold=0.5,
        time_window_sec=10,
        recovery_timeout_ms=3000,
        min_request_amount=5
    )
    Sentinel.load_degrade_rules([rule])
    
    for i in range(20):
        try:
            with Sentinel.entry("unstable_api"):
                # Simulate 60% error rate
                if random.random() < 0.6:
                    raise Exception("Service error")
                print(f"Request {i+1}: Success")
        except Exception as e:
            print(f"Request {i+1}: Failed - {e}")
        
        time.sleep(0.2)
    
    Sentinel.clear_rules()


def test_slow_request_breaker():
    """Test slow request based circuit breaker."""
    print("\n=== Slow Request Circuit Breaker ===")
    
    # Open circuit when slow requests > 50%
    rule = CircuitBreakerRule(
        resource="slow_api",
        strategy=CircuitBreakerStrategy.SLOW_REQUEST_RATIO,
        threshold=0.5,
        max_rt=100,  # 100ms threshold
        time_window_sec=10,
        recovery_timeout_ms=3000,
        min_request_amount=5
    )
    Sentinel.load_degrade_rules([rule])
    
    for i in range(20):
        try:
            with Sentinel.entry("slow_api"):
                # Simulate slow response
                time.sleep(0.15 if random.random() < 0.7 else 0.05)
                print(f"Request {i+1}: Success")
        except Exception as e:
            print(f"Request {i+1}: Failed - {e}")
        
        time.sleep(0.2)
    
    Sentinel.clear_rules()


if __name__ == "__main__":
    test_error_ratio_breaker()
    test_slow_request_breaker()
    print("\nAll tests completed!")
