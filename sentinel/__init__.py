"""
Sentinel-Py: Python version of Alibaba Sentinel

A powerful flow control, circuit breaking and system protection library
for microservices and distributed systems.

Example:
    >>> from sentinel import Sentinel
    >>> from sentinel.flow import FlowRule
    >>> 
    >>> # Define flow control rule
    >>> rule = FlowRule(resource="hello", qps=100)
    >>> Sentinel.load_rules([rule])
    >>> 
    >>> # Protect your code
    >>> with Sentinel.entry("hello"):
    >>>     print("Hello World")
"""

from .core.sentinel import Sentinel
from .core.context import Context, ContextUtil
from .core.resource import Resource
from .core.exceptions import (
    SentinelException,
    FlowException,
    DegradeException,
    SystemException,
    BlockException,
)
from .core.slot_chain import SlotChain
from .stat.statistics import Statistics

__version__ = "0.1.0"
__all__ = [
    "Sentinel",
    "Context",
    "ContextUtil",
    "Resource",
    "SentinelException",
    "FlowException",
    "DegradeException",
    "SystemException",
    "BlockException",
    "SlotChain",
    "Statistics",
]
