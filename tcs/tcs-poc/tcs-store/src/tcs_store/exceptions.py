"""Custom exceptions for TCS Store."""


class TCSStoreException(Exception):
    """Base exception for TCS Store."""
    pass


class TradeNotFoundError(TCSStoreException):
    """Raised when a trade ID is not found."""
    pass


class TradeAlreadyExistsError(TCSStoreException):
    """Raised when attempting to create a trade that already exists."""
    pass


class InvalidFilterError(TCSStoreException):
    """Raised when a filter is malformed or invalid."""
    pass


class InvalidContextError(TCSStoreException):
    """Raised when context metadata is invalid."""
    pass
