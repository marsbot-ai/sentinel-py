"""
System protection slot for checking system rules.
"""
from typing import Optional
from ..core.slot_chain import ProcessorSlot
from ..core.resource import ResourceWrapper
from ..core.context import Context
from ..core.exceptions import SystemException
from .rule import SystemRuleManager


class SystemSlot(ProcessorSlot):
    """
    Slot for system protection.
    
    Checks system metrics and blocks requests if system is overloaded.
    """
    
    def entry(self, resource: ResourceWrapper, context: Context) -> Optional[SystemException]:
        """Check system rules."""
        if not SystemRuleManager.check_system():
            return SystemException(
                resource=resource.get_resource().get_name(),
                message="System protection triggered - system is overloaded"
            )
        return None
    
    def exit(self, resource: ResourceWrapper, context: Context):
        """Exit system protection."""
        pass
