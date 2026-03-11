"""
Custom exceptions for Sentinel.
"""


class SentinelException(Exception):
    """Base exception for Sentinel."""
    
    def __init__(self, message: str = "", resource: str = ""):
        super().__init__(message)
        self.message = message
        self.resource = resource
    
    def __str__(self) -> str:
        return f"[{self.__class__.__name__}] resource={self.resource}, message={self.message}"


class BlockException(SentinelException):
    """Exception raised when request is blocked by Sentinel rules."""
    pass


class FlowException(BlockException):
    """Exception raised when request is blocked by flow control rules."""
    
    def __init__(self, resource: str = "", message: str = "Flow control limit exceeded"):
        super().__init__(message, resource)
        self.limit_type = "QPS"


class DegradeException(BlockException):
    """Exception raised when request is blocked by circuit breaker."""
    
    def __init__(self, resource: str = "", message: str = "Circuit breaker is open"):
        super().__init__(message, resource)


class SystemException(BlockException):
    """Exception raised when request is blocked by system protection rules."""
    
    def __init__(self, resource: str = "", message: str = "System protection triggered"):
        super().__init__(message, resource)


class ParamFlowException(BlockException):
    """Exception raised when request is blocked by parameter flow rules."""
    
    def __init__(self, resource: str = "", message: str = "Parameter flow limit exceeded"):
        super().__init__(message, resource)


class AuthorityException(BlockException):
    """Exception raised when request is blocked by authority rules."""
    
    def __init__(self, resource: str = "", message: str = "Access denied"):
        super().__init__(message, resource)
