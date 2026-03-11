"""
Circuit breaker slot for checking circuit breaker rules.
"""
from typing import Optional
from ..core.slot_chain import ProcessorSlot
from ..core.resource import ResourceWrapper
from ..core.context import Context
from ..core.exceptions import DegradeException
from .breaker import CircuitBreakerManager


class CircuitBreakerSlot(ProcessorSlot):
    """
    Slot for circuit breaker.
    
    Checks circuit breaker state and blocks requests if circuit is open.
    """
    
    def entry(self, resource: ResourceWrapper, context: Context) -> Optional[DegradeException]:
        """Check circuit breaker."""
        resource_name = resource.get_resource().get_name()
        breaker = CircuitBreakerManager.get_breaker(resource_name)
        
        if breaker:
            if not breaker.can_pass():
                return DegradeException(
                    resource=resource_name,
                    message=f"Circuit breaker is open for {resource_name}"
                )
        
        return None
    
    def exit(self, resource: ResourceWrapper, context: Context):
        """Update circuit breaker statistics."""
        resource_name = resource.get_resource().get_name()
        breaker = CircuitBreakerManager.get_breaker(resource_name)
        
        if breaker:
            entry = context.cur_entry
            if entry:
                if entry.block_error:
                    breaker.record_error(entry.rt)
                elif entry.error:
                    breaker.record_error(entry.rt)
                else:
                    breaker.record_success(entry.rt)
