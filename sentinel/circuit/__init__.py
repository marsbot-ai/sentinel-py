"""
Circuit breaker module for Sentinel.
"""
from .breaker import CircuitBreaker, CircuitBreakerRule, CircuitBreakerStrategy

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerRule",
    "CircuitBreakerStrategy",
]
