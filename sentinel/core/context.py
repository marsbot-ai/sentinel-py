"""
Context management for Sentinel.
"""
import threading
from typing import Optional, Dict, Any
from .resource import Resource


class Context:
    """
    Context for a single request through Sentinel.
    
    Each entry creates a new context that tracks the request lifecycle.
    """
    
    def __init__(self, name: str = ""):
        self.name = name
        self.resource: Optional[Resource] = None
        self.cur_entry: Optional['Entry'] = None
        self.origin: str = ""  # Origin (caller)
        self._attributes: Dict[str, Any] = {}
    
    def set_resource(self, resource: Resource):
        """Set current resource."""
        self.resource = resource
    
    def get_resource(self) -> Optional[Resource]:
        """Get current resource."""
        return self.resource
    
    def set_origin(self, origin: str):
        """Set origin (caller)."""
        self.origin = origin
    
    def get_origin(self) -> str:
        """Get origin."""
        return self.origin
    
    def set_attribute(self, key: str, value: Any):
        """Set context attribute."""
        self._attributes[key] = value
    
    def get_attribute(self, key: str) -> Optional[Any]:
        """Get context attribute."""
        return self._attributes.get(key)
    
    def __str__(self) -> str:
        return f"Context[name={self.name}, resource={self.resource}]"


class Entry:
    """
    Represents an entry into a protected resource.
    
    Tracks the lifecycle of a request through Sentinel.
    """
    
    def __init__(self, resource: Resource, context: Context):
        self.resource = resource
        self.context = context
        self.completed = False
        self.block_error: Optional[Exception] = None
        self.rt = 0  # Response time
        self.success = True
        self.error: Optional[Exception] = None
    
    def exit(self):
        """Mark entry as completed."""
        if not self.completed:
            self.completed = True
    
    def set_block_error(self, error: Exception):
        """Set block error."""
        self.block_error = error
        self.success = False
    
    def set_error(self, error: Exception):
        """Set business error."""
        self.error = error
        self.success = False
    
    def set_rt(self, rt: int):
        """Set response time in milliseconds."""
        self.rt = rt


class ContextUtil:
    """
    Utility class for context management.
    
    Manages thread-local contexts.
    """
    
    _thread_local = threading.local()
    _context_holder: Dict[int, Context] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_context(cls) -> Optional[Context]:
        """Get current thread's context."""
        thread_id = threading.current_thread().ident
        return cls._context_holder.get(thread_id)
    
    @classmethod
    def set_context(cls, context: Context):
        """Set current thread's context."""
        thread_id = threading.current_thread().ident
        with cls._lock:
            cls._context_holder[thread_id] = context
    
    @classmethod
    def remove_context(cls):
        """Remove current thread's context."""
        thread_id = threading.current_thread().ident
        with cls._lock:
            if thread_id in cls._context_holder:
                del cls._context_holder[thread_id]
    
    @classmethod
    def reset(cls):
        """Reset all contexts."""
        with cls._lock:
            cls._context_holder.clear()
