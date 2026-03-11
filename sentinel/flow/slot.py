"""
Flow control slot for checking flow rules.
"""
from typing import Optional
from ..core.slot_chain import ProcessorSlot
from ..core.resource import ResourceWrapper
from ..core.context import Context
from ..core.exceptions import FlowException
from .rule import FlowRuleManager, FlowRule


class FlowSlot(ProcessorSlot):
    """
    Slot for flow control.
    
    Checks flow rules and blocks requests if limit exceeded.
    """
    
    def entry(self, resource: ResourceWrapper, context: Context) -> Optional[FlowException]:
        """Check flow rules."""
        resource_name = resource.get_resource().get_name()
        rules = FlowRuleManager.get_rules_for_resource(resource_name)
        
        for rule in rules:
            if not rule.can_pass():
                return FlowException(
                    resource=resource_name,
                    message=f"Flow limit exceeded for {resource_name}"
                )
        
        return None
    
    def exit(self, resource: ResourceWrapper, context: Context):
        """Exit flow control."""
        pass
