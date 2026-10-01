"""Application errors exposed by OrderFlow operations."""


class OrderFlowError(Exception):
    """Base class for expected OrderFlow failures."""


class ValidationError(OrderFlowError):
    """Input does not satisfy a domain requirement."""


class NotFoundError(OrderFlowError):
    """A requested entity does not exist."""


class InvalidOperationError(OrderFlowError):
    """An operation is not allowed in the entity's current state."""
