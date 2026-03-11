"""
Leap array metric for sliding window statistics.
"""
import time
import threading
from typing import List, Optional
from .metric_bucket import MetricBucket


class WindowWrap:
    """A time window wrapper."""
    
    def __init__(self, window_length_ms: int, window_start: int):
        self.window_length_ms = window_length_ms
        self.window_start = window_start
        self.value: Optional[MetricBucket] = None
    
    def set_value(self, value: MetricBucket):
        """Set bucket value."""
        self.value = value
    
    def get_value(self) -> Optional[MetricBucket]:
        """Get bucket value."""
        return self.value
    
    def is_time_in_window(self, time_ms: int) -> bool:
        """Check if time is within this window."""
        return (self.window_start <= time_ms < 
                self.window_start + self.window_length_ms)
    
    def reset_to(self, start_time: int):
        """Reset window to new start time."""
        self.window_start = start_time
        if self.value:
            self.value.reset()


class LeapArrayMetric:
    """
    Leap array implementation for sliding window metrics.
    
    Provides O(1) time complexity for metric updates.
    """
    
    def __init__(self, window_length_ms: int, sample_count: int):
        """
        Initialize leap array.
        
        Args:
            window_length_ms: Length of each window in milliseconds
            sample_count: Number of windows to keep
        """
        self.window_length_ms = window_length_ms
        self.sample_count = sample_count
        self.interval_ms = window_length_ms * sample_count
        
        self._array: List[WindowWrap] = [None] * sample_count
        self._lock = threading.RLock()
    
    def _calculate_time_idx(self, time_ms: int) -> int:
        """Calculate array index for time."""
        time_id = time_ms // self.window_length_ms
        return int(time_id % self.sample_count)
    
    def _calculate_window_start(self, time_ms: int) -> int:
        """Calculate window start time."""
        return time_ms - (time_ms % self.window_length_ms)
    
    def current_window(self, time_ms: int) -> WindowWrap:
        """Get current window for time."""
        idx = self._calculate_time_idx(time_ms)
        window_start = self._calculate_window_start(time_ms)
        
        with self._lock:
            old = self._array[idx]
            
            if old is None:
                # Create new window
                wrap = WindowWrap(self.window_length_ms, window_start)
                wrap.set_value(MetricBucket())
                self._array[idx] = wrap
                return wrap
            elif old.window_start == window_start:
                # Reuse current window
                return old
            elif old.window_start < window_start:
                # Window expired, reset it
                old.reset_to(window_start)
                return old
            else:
                # Should not happen - clock moved backwards
                return old
    
    def get_window_value(self, time_ms: int) -> Optional[MetricBucket]:
        """Get bucket value for time."""
        idx = self._calculate_time_idx(time_ms)
        
        with self._lock:
            wrap = self._array[idx]
            if wrap is None or not wrap.is_time_in_window(time_ms):
                return None
            return wrap.get_value()
    
    def values(self) -> List[MetricBucket]:
        """Get all valid window values."""
        current_time = int(time.time() * 1000)
        result = []
        
        with self._lock:
            for wrap in self._array:
                if (wrap is not None and 
                    wrap.get_value() is not None and
                    current_time - wrap.window_start < self.interval_ms):
                    result.append(wrap.get_value())
        
        return result
    
    def get_sum(self, metric: str) -> int:
        """Get sum of metric across all windows."""
        values = self.values()
        return sum(v.get(metric) for v in values)
    
    def get_avg(self, metric: str) -> float:
        """Get average of metric."""
        values = self.values()
        if not values:
            return 0.0
        return sum(v.get(metric) for v in values) / len(values)
