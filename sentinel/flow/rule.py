"""
Flow control rules for Sentinel.
"""
import threading
import time
from typing import List, Optional, Dict
from enum import Enum


class ControlBehavior(Enum):
    """Control behavior types."""
    DEFAULT = 0  # Direct rejection
    WARM_UP = 1  # Warm up
    RATE_LIMITER = 2  # Uniform rate limiting
    WARM_UP_RATE_LIMITER = 3  # Warm up + rate limiting


class FlowRule:
    """
    Rule for flow control (QPS/Concurrency limiting).
    
    Example:
        >>> # Limit to 100 QPS
        >>> rule = FlowRule(resource="api", qps=100)
        >>> 
        >>> # Limit concurrency to 50
        >>> rule = FlowRule(resource="api", thread_count=50)
        >>> 
        >>> # Warm up from 10 to 100 QPS over 10 seconds
        >>> rule = FlowRule(
        ...     resource="api",
        ...     qps=100,
        ...     control_behavior=ControlBehavior.WARM_UP,
        ...     warm_up_period_sec=10,
        ...     cold_factor=3
        ... )
    """
    
    def __init__(
        self,
        resource: str,
        qps: Optional[float] = None,
        thread_count: Optional[int] = None,
        control_behavior: ControlBehavior = ControlBehavior.DEFAULT,
        warm_up_period_sec: int = 10,
        cold_factor: int = 3,
        max_queueing_time_ms: int = 500,
    ):
        """
        Initialize flow rule.
        
        Args:
            resource: Resource name to protect
            qps: QPS limit (queries per second)
            thread_count: Concurrent thread limit
            control_behavior: Control behavior type
            warm_up_period_sec: Warm up period in seconds
            cold_factor: Cold factor for warm up
            max_queueing_time_ms: Max queueing time for rate limiter
        """
        self.resource = resource
        self.qps = qps
        self.thread_count = thread_count
        self.control_behavior = control_behavior
        self.warm_up_period_sec = warm_up_period_sec
        self.cold_factor = cold_factor
        self.max_queueing_time_ms = max_queueing_time_ms
        
        # Token bucket for QPS limiting
        self._tokens = qps if qps else 0
        self._last_refill_time = time.time()
        self._lock = threading.Lock()
        
        # For warm up
        self._warm_up_started = False
        self._warm_up_start_time = 0
    
    def can_pass(self, acquire_count: int = 1) -> bool:
        """
        Check if request can pass.
        
        Args:
            acquire_count: Number of tokens to acquire
            
        Returns:
            True if request can pass
        """
        if self.qps is not None:
            return self._check_qps(acquire_count)
        
        if self.thread_count is not None:
            return self._check_thread_count()
        
        return True
    
    def _check_qps(self, acquire_count: int) -> bool:
        """Check QPS limit using token bucket."""
        with self._lock:
            now = time.time()
            
            # Handle warm up
            if self.control_behavior == ControlBehavior.WARM_UP:
                current_qps = self._get_warm_up_qps(now)
            else:
                current_qps = self.qps
            
            # Refill tokens
            elapsed = now - self._last_refill_time
            tokens_to_add = elapsed * current_qps
            self._tokens = min(current_qps, self._tokens + tokens_to_add)
            self._last_refill_time = now
            
            # Check if we have enough tokens
            if self._tokens >= acquire_count:
                self._tokens -= acquire_count
                return True
            
            return False
    
    def _get_warm_up_qps(self, now: float) -> float:
        """Get current QPS during warm up."""
        if not self._warm_up_started:
            self._warm_up_started = True
            self._warm_up_start_time = now
            return self.qps / self.cold_factor
        
        elapsed = now - self._warm_up_start_time
        if elapsed >= self.warm_up_period_sec:
            return self.qps
        
        # Linear warm up
        warm_up_progress = elapsed / self.warm_up_period_sec
        cold_qps = self.qps / self.cold_factor
        return cold_qps + (self.qps - cold_qps) * warm_up_progress
    
    def _check_thread_count(self) -> bool:
        """Check concurrent thread limit."""
        from ..stat.statistics import Statistics
        
        current_threads = Statistics.get_instance().get_thread_count(self.resource)
        return current_threads <= self.thread_count
    
    def __str__(self) -> str:
        return (f"FlowRule[{self.resource}: "
                f"qps={self.qps}, "
                f"threads={self.thread_count}, "
                f"behavior={self.control_behavior.name}]")


class FlowRuleManager:
    """Manager for flow rules."""
    
    _rules: Dict[str, List[FlowRule]] = {}
    _lock = threading.RLock()
    
    @classmethod
    def load_rules(cls, rules: List[FlowRule]):
        """Load flow rules."""
        with cls._lock:
            cls._rules.clear()
            for rule in rules:
                if rule.resource not in cls._rules:
                    cls._rules[rule.resource] = []
                cls._rules[rule.resource].append(rule)
    
    @classmethod
    def get_rules_for_resource(cls, resource: str) -> List[FlowRule]:
        """Get rules for a resource."""
        with cls._lock:
            return cls._rules.get(resource, [])
    
    @classmethod
    def clear_rules(cls):
        """Clear all rules."""
        with cls._lock:
            cls._rules.clear()
