"""
Metric bucket for sliding window statistics.
"""
import threading
from typing import Dict


class MetricBucket:
    """
    A bucket for collecting metrics in a time window.
    
    Tracks:
    - Success count
    - Exception count
    - Block count
    - Pass count
    - RT (response time)
    """
    
    def __init__(self):
        self._counters: Dict[str, int] = {
            "success": 0,
            "exception": 0,
            "block": 0,
            "pass": 0,
            "rt": 0,  # Total response time
        }
        self._lock = threading.Lock()
    
    def add_success(self, count: int = 1):
        """Add successful request."""
        with self._lock:
            self._counters["success"] += count
    
    def add_exception(self, count: int = 1):
        """Add exception request."""
        with self._lock:
            self._counters["exception"] += count
    
    def add_block(self, count: int = 1):
        """Add blocked request."""
        with self._lock:
            self._counters["block"] += count
    
    def add_pass(self, count: int = 1):
        """Add passed request."""
        with self._lock:
            self._counters["pass"] += count
    
    def add_rt(self, rt: int):
        """Add response time."""
        with self._lock:
            self._counters["rt"] += rt
    
    def get(self, metric: str) -> int:
        """Get metric value."""
        with self._lock:
            return self._counters.get(metric, 0)
    
    def get_success(self) -> int:
        """Get success count."""
        return self.get("success")
    
    def get_exception(self) -> int:
        """Get exception count."""
        return self.get("exception")
    
    def get_block(self) -> int:
        """Get block count."""
        return self.get("block")
    
    def get_pass(self) -> int:
        """Get pass count."""
        return self.get("pass")
    
    def get_rt(self) -> int:
        """Get total response time."""
        return self.get("rt")
    
    def reset(self):
        """Reset all counters."""
        with self._lock:
            for key in self._counters:
                self._counters[key] = 0
    
    def copy(self) -> 'MetricBucket':
        """Create a copy of this bucket."""
        new_bucket = MetricBucket()
        with self._lock:
            new_bucket._counters = self._counters.copy()
        return new_bucket
