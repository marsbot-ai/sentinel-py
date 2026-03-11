"""
Slot chain for processing requests through Sentinel rules.
"""
from typing import List, Optional
from .resource import ResourceWrapper
from .context import Context
from .exceptions import SentinelException, BlockException
from ..flow.slot import FlowSlot
from ..circuit.slot import CircuitBreakerSlot
from ..system.slot import SystemSlot
from ..stat.slot import StatisticSlot


class ProcessorSlot:
    """Base class for processor slots."""
    
    def entry(self, resource: ResourceWrapper, context: Context) -> Optional[BlockException]:
        """Process entry. Returns BlockException if blocked."""
        raise NotImplementedError
    
    def exit(self, resource: ResourceWrapper, context: Context):
        """Process exit."""
        pass


class SlotChain:
    """
    Chain of processor slots.
    
    Each request flows through the chain, with each slot performing
    its specific checks (flow control, circuit breaking, etc.).
    """
    
    def __init__(self):
        self._slots: List[ProcessorSlot] = [
            StatisticSlot(),      # Statistics first
            SystemSlot(),         # System protection
            FlowSlot(),           # Flow control
            CircuitBreakerSlot(), # Circuit breaking
        ]
    
    def entry(self, resource: ResourceWrapper, context: Context):
        """
        Process entry through the chain.
        
        Args:
            resource: Resource wrapper
            context: Request context
            
        Raises:
            BlockException: If any slot blocks the request
        """
        for slot in self._slots:
            exception = slot.entry(resource, context)
            if exception:
                raise exception
    
    def exit(self, resource: ResourceWrapper, context: Context):
        """Process exit through the chain."""
        for slot in reversed(self._slots):
            try:
                slot.exit(resource, context)
            except Exception:
                pass  # Ignore exit errors
