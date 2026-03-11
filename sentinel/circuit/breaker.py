"""
Circuit breaker implementation for Sentinel.
"""
import threading
import time
from enum import Enum
from typing import Dict, List, Optional


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = 0  # Normal operation
    OPEN = 1    # Circuit open (blocking requests)
    HALF_OPEN = 2  # Testing if service recovered


class CircuitBreakerStrategy(Enum):
    """Circuit breaker strategies."""
    SLOW_REQUEST_RATIO = 0  # Based on slow request ratio
    ERROR_RATIO = 1         # Based on error ratio
    ERROR_COUNT = 2         # Based on error count


class CircuitBreakerRule:
    """
    Rule for circuit breaker.
    
    Example:
        >>> # Break when error ratio > 50%
        >>> rule = CircuitBreakerRule(
        ...     resource="api",
        ...     strategy=CircuitBreakerStrategy.ERROR_RATIO,
        ...     threshold=0.5,
        ...     time_window_sec=10
        ... )
        >>> 
        >>> # Break when slow requests > 80%
        >>> rule = CircuitBreakerRule(
        ...     resource="api",
        ...     strategy=CircuitBreakerStrategy.SLOW_REQUEST_RATIO,
        ...     threshold=0.8,
        ...     max_rt=500,  # ms
        ...     time_window_sec=10
        ... )
    """
    
    def __init__(
        self,
        resource: str,
        strategy: CircuitBreakerStrategy = CircuitBreakerStrategy.ERROR_RATIO,
        threshold: float = 0.5,
        time_window_sec: int = 10,
        recovery_timeout_ms: int = 5000,
        min_request_amount: int = 5,
        max_rt: Optional[int] = None,  # For slow request strategy
    ):
        """
        Initialize circuit breaker rule.
        
        Args:
            resource: Resource name
            strategy: Circuit breaker strategy
            threshold: Threshold for triggering circuit break
            time_window_sec: Time window for statistics
            recovery_timeout_ms: Time before attempting recovery
            min_request_amount: Minimum requests before triggering
            max_rt: Max RT for slow request detection (ms)
        """
        self.resource = resource
        self.strategy = strategy
        self.threshold = threshold
        self.time_window_sec = time_window_sec
        self.recovery_timeout_ms = recovery_timeout_ms
        self.min_request_amount = min_request_amount
        self.max_rt = max_rt


class CircuitBreaker:
    """
    Circuit breaker implementation.
    
    Monitors request metrics and opens circuit when threshold exceeded.
    """
    
    def __init__(self, rule: CircuitBreakerRule):
        self.rule = rule
        self.state = CircuitBreakerState.CLOSED
        self._state_lock = threading.RLock()
        
        # Statistics
        self._success_count = 0
        self._error_count = 0
        self._slow_count = 0
        self._total_count = 0
        self._window_start = time.time()
        self._stats_lock = threading.Lock()
        
        # Recovery tracking
        self._open_time = 0
        self._half_open_probes = 0
    
    def can_pass(self) -> bool:
        """Check if request can pass."""
        with self._state_lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if we should try recovery
                if time.time() * 1000 - self._open_time >= self.rule.recovery_timeout_ms:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self._half_open_probes = 0
                    return True
                return False
            elif self.state == CircuitBreakerState.HALF_OPEN:
                # Allow limited probes
                self._half_open_probes += 1
                return self._half_open_probes <= 3
        
        return True
    
    def record_success(self, rt: int = 0):
        """Record successful request."""
        with self._stats_lock:
            self._reset_window_if_needed()
            self._success_count += 1
            self._total_count += 1
            
            if self.rule.max_rt and rt > self.rule.max_rt:
                self._slow_count += 1
        
        self._check_state_transition(True)
    
    def record_error(self, rt: int = 0):
        """Record failed request."""
        with self._stats_lock:
            self._reset_window_if_needed()
            self._error_count += 1
            self._total_count += 1
            
            if self.rule.max_rt and rt > self.rule.max_rt:
                self._slow_count += 1
        
        self._check_state_transition(False)
    
    def _reset_window_if_needed(self):
        """Reset statistics window if expired."""
        now = time.time()
        if now - self._window_start >= self.rule.time_window_sec:
            self._success_count = 0
            self._error_count = 0
            self._slow_count = 0
            self._total_count = 0
            self._window_start = now
    
    def _check_state_transition(self, success: bool):
        """Check and update circuit breaker state."""
        with self._state_lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                if success:
                    # Success in half-open, close circuit
                    self.state = CircuitBreakerState.CLOSED
                    self._half_open_probes = 0
                else:
                    # Failure in half-open, open again
                    self.state = CircuitBreakerState.OPEN
                    self._open_time = time.time() * 1000
            
            elif self.state == CircuitBreakerState.CLOSED:
                # Check if we should open
                if self._should_open():
                    self.state = CircuitBreakerState.OPEN
                    self._open_time = time.time() * 1000
    
    def _should_open(self) -> bool:
        """Check if circuit should open."""
        with self._stats_lock:
            if self._total_count < self.rule.min_request_amount:
                return False
            
            if self.rule.strategy == CircuitBreakerStrategy.ERROR_RATIO:
                if self._total_count == 0:
                    return False
                ratio = self._error_count / self._total_count
                return ratio >= self.rule.threshold
            
            elif self.rule.strategy == CircuitBreakerStrategy.ERROR_COUNT:
                return self._error_count >= self.rule.threshold
            
            elif self.rule.strategy == CircuitBreakerStrategy.SLOW_REQUEST_RATIO:
                if self._total_count == 0:
                    return False
                ratio = self._slow_count / self._total_count
                return ratio >= self.rule.threshold
        
        return False
    
    def get_state(self) -> CircuitBreakerState:
        """Get current state."""
        with self._state_lock:
            return self.state
    
    def __str__(self) -> str:
        return (f"CircuitBreaker[{self.rule.resource}: "
                f"state={self.state.name}, "
                f"strategy={self.rule.strategy.name}]")


class CircuitBreakerManager:
    """Manager for circuit breakers."""
    
    _breakers: Dict[str, CircuitBreaker] = {}
    _lock = threading.RLock()
    
    @classmethod
    def get_breaker(cls, resource: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker for resource."""
        with cls._lock:
            return cls._breakers.get(resource)
    
    @classmethod
    def load_rules(cls, rules: List[CircuitBreakerRule]):
        """Load circuit breaker rules."""
        with cls._lock:
            cls._breakers.clear()
            for rule in rules:
                cls._breakers[rule.resource] = CircuitBreaker(rule)
    
    @classmethod
    def clear_rules(cls):
        """Clear all rules."""
        with cls._lock:
            cls._breakers.clear()
