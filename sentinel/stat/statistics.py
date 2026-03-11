"""
Statistics collection and management.
"""
import threading
import time
from typing import Dict, Optional
from collections import defaultdict


class Statistics:
    """
    Global statistics for Sentinel.
    
    Tracks metrics for all resources.
    """
    
    _instance: Optional['Statistics'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._resource_stats: Dict[str, 'ResourceStatistics'] = {}
        self._lock = threading.RLock()
    
    @classmethod
    def get_instance(cls) -> 'Statistics':
        """Get singleton instance."""
        return cls()
    
    def _get_or_create_resource_stats(self, resource: str) -> 'ResourceStatistics':
        """Get or create statistics for a resource."""
        with self._lock:
            if resource not in self._resource_stats:
                self._resource_stats[resource] = ResourceStatistics(resource)
            return self._resource_stats[resource]
    
    def increase_thread_count(self, resource: str):
        """Increment concurrent thread count."""
        stats = self._get_or_create_resource_stats(resource)
        stats.increase_thread_count()
    
    def decrease_thread_count(self, resource: str):
        """Decrement concurrent thread count."""
        stats = self._get_or_create_resource_stats(resource)
        stats.decrease_thread_count()
    
    def add_success(self, resource: str):
        """Record a successful request."""
        stats = self._get_or_create_resource_stats(resource)
        stats.add_success()
    
    def add_exception(self, resource: str):
        """Record a failed request."""
        stats = self._get_or_create_resource_stats(resource)
        stats.add_exception()
    
    def add_rt(self, resource: str, rt: int):
        """Add response time."""
        stats = self._get_or_create_resource_stats(resource)
        stats.add_rt(rt)
    
    def get_qps(self, resource: str) -> float:
        """Get current QPS for a resource."""
        stats = self._get_or_create_resource_stats(resource)
        return stats.get_qps()
    
    def get_avg_rt(self, resource: str) -> float:
        """Get average response time."""
        stats = self._get_or_create_resource_stats(resource)
        return stats.get_avg_rt()
    
    def get_thread_count(self, resource: str) -> int:
        """Get current thread count."""
        stats = self._get_or_create_resource_stats(resource)
        return stats.get_thread_count()
    
    def get_success_count(self, resource: str) -> int:
        """Get success count."""
        stats = self._get_or_create_resource_stats(resource)
        return stats.get_success_count()
    
    def get_exception_count(self, resource: str) -> int:
        """Get exception count."""
        stats = self._get_or_create_resource_stats(resource)
        return stats.get_exception_count()
    
    def get_all_resources(self) -> Dict[str, 'ResourceStatistics']:
        """Get statistics for all resources."""
        with self._lock:
            return self._resource_stats.copy()


class ResourceStatistics:
    """Statistics for a single resource."""
    
    def __init__(self, resource: str):
        self.resource = resource
        self._thread_count = 0
        self._success_count = 0
        self._exception_count = 0
        self._total_rt = 0
        self._lock = threading.RLock()
        
        # Sliding window for QPS calculation
        self._window_size = 1  # 1 second
        self._window_start = time.time()
        self._window_count = 0
    
    def increase_thread_count(self):
        """Increment concurrent thread count."""
        with self._lock:
            self._thread_count += 1
    
    def decrease_thread_count(self):
        """Decrement concurrent thread count."""
        with self._lock:
            self._thread_count = max(0, self._thread_count - 1)
    
    def add_success(self):
        """Record successful request."""
        with self._lock:
            self._success_count += 1
            self._update_window()
            self._window_count += 1
    
    def add_exception(self):
        """Record failed request."""
        with self._lock:
            self._exception_count += 1
            self._update_window()
    
    def add_rt(self, rt: int):
        """Add response time."""
        with self._lock:
            self._total_rt += rt
    
    def _update_window(self):
        """Update sliding window."""
        now = time.time()
        if now - self._window_start >= self._window_size:
            self._window_start = now
            self._window_count = 0
    
    def get_qps(self) -> float:
        """Get current QPS."""
        with self._lock:
            self._update_window()
            return self._window_count / self._window_size
    
    def get_avg_rt(self) -> float:
        """Get average response time."""
        with self._lock:
            total = self._success_count + self._exception_count
            if total == 0:
                return 0.0
            return self._total_rt / total
    
    def get_thread_count(self) -> int:
        """Get current thread count."""
        with self._lock:
            return self._thread_count
    
    def get_success_count(self) -> int:
        """Get success count."""
        with self._lock:
            return self._success_count
    
    def get_exception_count(self) -> int:
        """Get exception count."""
        with self._lock:
            return self._exception_count
    
    def __str__(self) -> str:
        return (f"ResourceStats[{self.resource}: "
                f"threads={self._thread_count}, "
                f"success={self._success_count}, "
                f"exception={self._exception_count}, "
                f"qps={self.get_qps():.2f}]")
