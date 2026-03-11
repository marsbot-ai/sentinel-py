"""
Traffic shaping strategies for flow control.
"""
from enum import Enum


class TrafficShapingStrategy(Enum):
    """Traffic shaping strategies."""
    FAST_FAIL = 0  # Fast fail when limit exceeded
    WARM_UP = 1  # Gradual increase to threshold
    LINEAR = 2  # Linear increase
    SMOOTH = 3  # Smooth rate limiting


class RateLimiter:
    """
    Smooth rate limiter using leaky bucket algorithm.
    
    Provides uniform traffic shaping.
    """
    
    def __init__(self, qps: float):
        self.qps = qps
        self.interval_ms = 1000.0 / qps if qps > 0 else 0
        self._last_pass_time = 0
    
    def can_pass(self, now: int) -> bool:
        """Check if request can pass at given time."""
        if self._last_pass_time == 0:
            self._last_pass_time = now
            return True
        
        expected_time = self._last_pass_time + self.interval_ms
        if now >= expected_time:
            self._last_pass_time = now
            return True
        
        return False
    
    def get_wait_time(self, now: int) -> int:
        """Get wait time in milliseconds."""
        if self._last_pass_time == 0:
            return 0
        
        expected_time = self._last_pass_time + self.interval_ms
        wait_time = expected_time - now
        return max(0, int(wait_time))
