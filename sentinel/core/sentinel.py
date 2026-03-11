"""
Main Sentinel class - entry point for the library.
"""
from typing import List, Optional, Callable, Any, Dict
import threading
import logging

from .resource import Resource, ResourceWrapper
from .context import Context, ContextUtil, Entry
from .slot_chain import SlotChain
from .exceptions import SentinelException, BlockException
from ..flow.rule import FlowRule
from ..circuit.breaker import CircuitBreakerRule
from ..system.rule import SystemRule

logger = logging.getLogger(__name__)


class Sentinel:
    """
    Main entry point for Sentinel library.
    
    Provides flow control, circuit breaking, and system protection.
    
    Example:
        >>> from sentinel import Sentinel
        >>> from sentinel.flow import FlowRule
        >>> 
        >>> # Configure rules
        >>> rule = FlowRule(resource="api", qps=100)
        >>> Sentinel.load_flow_rules([rule])
        >>> 
        >>> # Protect code
        >>> with Sentinel.entry("api"):
        >>>     process_request()
    """
    
    _instance: Optional['Sentinel'] = None
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
        self._slot_chain = SlotChain()
        self._flow_rules: Dict[str, List[FlowRule]] = {}
        self._degrade_rules: Dict[str, List[CircuitBreakerRule]] = {}
        self._system_rules: List[SystemRule] = []
        self._rule_lock = threading.RLock()
    
    @classmethod
    def entry(cls, resource_name: str, entry_type: str = "OUT"):
        """
        Create an entry for a protected resource.
        
        Args:
            resource_name: Name of the resource
            entry_type: Type of entry (IN or OUT)
            
        Returns:
            Entry context manager
            
        Example:
            >>> with Sentinel.entry("my_api"):
            >>>     do_something()
        """
        return _EntryContextManager(resource_name, entry_type)
    
    @classmethod
    def load_flow_rules(cls, rules: List[FlowRule]):
        """
        Load flow control rules.
        
        Args:
            rules: List of FlowRule objects
        """
        instance = cls()
        with instance._rule_lock:
            instance._flow_rules.clear()
            for rule in rules:
                resource = rule.resource
                if resource not in instance._flow_rules:
                    instance._flow_rules[resource] = []
                instance._flow_rules[resource].append(rule)
        logger.info(f"Loaded {len(rules)} flow rules")
    
    @classmethod
    def load_degrade_rules(cls, rules: List[CircuitBreakerRule]):
        """
        Load circuit breaker rules.
        
        Args:
            rules: List of CircuitBreakerRule objects
        """
        instance = cls()
        with instance._rule_lock:
            instance._degrade_rules.clear()
            for rule in rules:
                resource = rule.resource
                if resource not in instance._degrade_rules:
                    instance._degrade_rules[resource] = []
                instance._degrade_rules[resource].append(rule)
        logger.info(f"Loaded {len(rules)} degrade rules")
    
    @classmethod
    def load_system_rules(cls, rules: List[SystemRule]):
        """
        Load system protection rules.
        
        Args:
            rules: List of SystemRule objects
        """
        instance = cls()
        with instance._rule_lock:
            instance._system_rules = rules
        logger.info(f"Loaded {len(rules)} system rules")
    
    @classmethod
    def get_flow_rules(cls, resource: str) -> List[FlowRule]:
        """Get flow rules for a resource."""
        instance = cls()
        with instance._rule_lock:
            return instance._flow_rules.get(resource, [])
    
    @classmethod
    def get_degrade_rules(cls, resource: str) -> List[CircuitBreakerRule]:
        """Get degrade rules for a resource."""
        instance = cls()
        with instance._rule_lock:
            return instance._degrade_rules.get(resource, [])
    
    @classmethod
    def get_system_rules(cls) -> List[SystemRule]:
        """Get all system rules."""
        instance = cls()
        with instance._rule_lock:
            return instance._system_rules[:]
    
    @classmethod
    def clear_rules(cls):
        """Clear all rules."""
        instance = cls()
        with instance._rule_lock:
            instance._flow_rules.clear()
            instance._degrade_rules.clear()
            instance._system_rules.clear()
        logger.info("All rules cleared")


class _EntryContextManager:
    """Context manager for Sentinel entries."""
    
    def __init__(self, resource_name: str, entry_type: str = "OUT"):
        self.resource_name = resource_name
        self.entry_type = entry_type
        self.entry: Optional[Entry] = None
        self.context: Optional[Context] = None
    
    def __enter__(self):
        """Enter the protected block."""
        from ..stat.statistics import Statistics
        
        # Create resource
        resource = Resource(self.resource_name)
        resource_wrapper = ResourceWrapper(resource, self.entry_type)
        
        # Create context
        self.context = Context()
        self.context.set_resource(resource)
        ContextUtil.set_context(self.context)
        
        # Create entry
        self.entry = Entry(resource, self.context)
        
        # Run slot chain
        sentinel = Sentinel()
        try:
            sentinel._slot_chain.entry(resource_wrapper, self.context)
            Statistics.get_instance().increase_thread_count(self.resource_name)
        except BlockException:
            raise
        
        return self.entry
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the protected block."""
        from ..stat.statistics import Statistics
        
        if self.entry:
            # Record error if any
            if exc_val:
                self.entry.set_error(exc_val)
            
            # Complete entry
            self.entry.exit()
            
            # Update statistics
            Statistics.get_instance().decrease_thread_count(self.resource_name)
            if exc_type is None:
                Statistics.get_instance().add_success(self.resource_name)
            else:
                Statistics.get_instance().add_exception(self.resource_name)
        
        # Clean up context
        ContextUtil.remove_context()
        
        # Don't suppress exceptions
        return False
