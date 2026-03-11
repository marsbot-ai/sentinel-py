"""
Statistic slot for collecting metrics.
"""
from ..core.slot_chain import ProcessorSlot
from ..core.resource import ResourceWrapper
from ..core.context import Context


class StatisticSlot(ProcessorSlot):
    """
    Slot for collecting runtime statistics.
    
    Tracks QPS, response time, success/error counts.
    """
    
    def entry(self, resource: ResourceWrapper, context: Context):
        """Record entry statistics."""
        from .statistics import Statistics
        
        resource_name = resource.get_resource().get_name()
        Statistics.get_instance().increase_thread_count(resource_name)
        return None
    
    def exit(self, resource: ResourceWrapper, context: Context):
        """Record exit statistics."""
        from .statistics import Statistics
        
        resource_name = resource.get_resource().get_name()
        Statistics.get_instance().decrease_thread_count(resource_name)
