"""
System protection rules for Sentinel.
"""
import threading
from typing import List, Optional
from enum import Enum


class SystemRuleType(Enum):
    """System rule types."""
    LOAD = 0
    CPU = 1
    RT = 2
    THREAD = 3
    QPS = 4


class SystemRule:
    """
    Rule for system protection.
    
    Protects the system from overload by limiting resource usage.
    
    Example:
        >>> # Protect when CPU > 80%
        >>> rule = SystemRule(highest_cpu_usage=0.8)
        >>> 
        >>> # Protect when system load > 4
        >>> rule = SystemRule(highest_system_load=4.0)
    """
    
    def __init__(
        self,
        highest_system_load: Optional[float] = None,
        highest_cpu_usage: Optional[float] = None,
        avg_rt: Optional[int] = None,
        max_thread: Optional[int] = None,
        qps: Optional[float] = None,
    ):
        """
        Initialize system rule.
        
        Args:
            highest_system_load: Max system load average
            highest_cpu_usage: Max CPU usage (0.0-1.0)
            avg_rt: Max average response time (ms)
            max_thread: Max thread count
            qps: Max QPS across all resources
        """
        self.highest_system_load = highest_system_load
        self.highest_cpu_usage = highest_cpu_usage
        self.avg_rt = avg_rt
        self.max_thread = max_thread
        self.qps = qps
    
    def check_system_status(self) -> bool:
        """
        Check if system status is within limits.
        
        Returns:
            True if system is healthy
        """
        from .metrics import SystemMetrics
        
        metrics = SystemMetrics.get_instance()
        
        if self.highest_system_load is not None:
            if metrics.get_system_load() > self.highest_system_load:
                return False
        
        if self.highest_cpu_usage is not None:
            if metrics.get_cpu_usage() > self.highest_cpu_usage:
                return False
        
        if self.avg_rt is not None:
            if metrics.get_avg_rt() > self.avg_rt:
                return False
        
        if self.max_thread is not None:
            if metrics.get_thread_count() > self.max_thread:
                return False
        
        if self.qps is not None:
            if metrics.get_qps() > self.qps:
                return False
        
        return True
    
    def __str__(self) -> str:
        return (f"SystemRule[load={self.highest_system_load}, "
                f"cpu={self.highest_cpu_usage}, "
                f"rt={self.avg_rt}, "
                f"threads={self.max_thread}, "
                f"qps={self.qps}]")


class SystemRuleManager:
    """Manager for system rules."""
    
    _rules: List[SystemRule] = []
    _lock = threading.RLock()
    
    @classmethod
    def load_rules(cls, rules: List[SystemRule]):
        """Load system rules."""
        with cls._lock:
            cls._rules = rules[:]
    
    @classmethod
    def get_rules(cls) -> List[SystemRule]:
        """Get all system rules."""
        with cls._lock:
            return cls._rules[:]
    
    @classmethod
    def clear_rules(cls):
        """Clear all rules."""
        with cls._lock:
            cls._rules.clear()
    
    @classmethod
    def check_system(cls) -> bool:
        """Check system against all rules."""
        with cls._lock:
            for rule in cls._rules:
                if not rule.check_system_status():
                    return False
        return True
