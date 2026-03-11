"""
Resource definition for Sentinel.
"""
from typing import Optional, Dict, Any
import threading


class Resource:
    """
    Represents a protected resource in Sentinel.
    
    A resource can be a method, an API endpoint, or any code block
    that needs protection.
    """
    
    def __init__(self, name: str, resource_type: str = "COMMON"):
        """
        Initialize a resource.
        
        Args:
            name: Unique resource name
            resource_type: Type of resource (COMMON, WEB, RPC, etc.)
        """
        self.name = name
        self.resource_type = resource_type
        self._metadata: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def get_name(self) -> str:
        """Get resource name."""
        return self.name
    
    def get_type(self) -> str:
        """Get resource type."""
        return self.resource_type
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata."""
        with self._lock:
            self._metadata[key] = value
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """Get metadata."""
        return self._metadata.get(key)
    
    def __str__(self) -> str:
        return f"Resource[name={self.name}, type={self.resource_type}]"
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Resource):
            return False
        return self.name == other.name


class ResourceWrapper:
    """Wrapper for resource with additional context."""
    
    def __init__(self, resource: Resource, entry_type: str = "OUT"):
        self.resource = resource
        self.entry_type = entry_type  # IN or OUT
    
    def get_resource(self) -> Resource:
        return self.resource
    
    def get_entry_type(self) -> str:
        return self.entry_type
