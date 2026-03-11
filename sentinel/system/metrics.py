"""
System metrics collection.
"""
import os
import time
import threading
import psutil
from typing import Optional


class SystemMetrics:
    """
    Collects system-level metrics.
    
    Tracks CPU, memory, load average, etc.
    """
    
    _instance: Optional['SystemMetrics'] = None
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
        self._cpu_percent = 0.0
        self._last_cpu_check = 0
        self._metrics_lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> 'SystemMetrics':
        """Get singleton instance."""
        return cls()
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage (0.0-1.0)."""
        with self._metrics_lock:
            # Throttle CPU checks to avoid overhead
            now = time.time()
            if now - self._last_cpu_check < 1:
                return self._cpu_percent
            
            try:
                self._cpu_percent = psutil.cpu_percent(interval=0.1) / 100.0
                self._last_cpu_check = now
            except Exception:
                pass
            
            return self._cpu_percent
    
    def get_memory_usage(self) -> float:
        """Get current memory usage (0.0-1.0)."""
        try:
            return psutil.virtual_memory().percent / 100.0
        except Exception:
            return 0.0
    
    def get_system_load(self) -> float:
        """Get system load average (1 minute)."""
        try:
            load1, _, _ = os.getloadavg()
            return load1
        except (OSError, AttributeError):
            return 0.0
    
    def get_thread_count(self) -> int:
        """Get total thread count."""
        try:
            return threading.active_count()
        except Exception:
            return 0
    
    def get_qps(self) -> float:
        """Get total QPS across all resources."""
        from ..stat.statistics import Statistics
        
        total_qps = 0.0
        stats = Statistics.get_instance()
        for resource in stats.get_all_resources().keys():
            total_qps += stats.get_qps(resource)
        
        return total_qps
    
    def get_avg_rt(self) -> float:
        """Get average response time across all resources."""
        from ..stat.statistics import Statistics
        
        stats = Statistics.get_instance()
        total_rt = 0.0
        count = 0
        
        for resource in stats.get_all_resources().keys():
            rt = stats.get_avg_rt(resource)
            if rt > 0:
                total_rt += rt
                count += 1
        
        return total_rt / count if count > 0 else 0.0
    
    def get_metrics(self) -> dict:
        """Get all system metrics."""
        return {
            "cpu_usage": self.get_cpu_usage(),
            "memory_usage": self.get_memory_usage(),
            "system_load": self.get_system_load(),
            "thread_count": self.get_thread_count(),
            "qps": self.get_qps(),
            "avg_rt": self.get_avg_rt(),
        }
