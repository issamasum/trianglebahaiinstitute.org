"""Exceptions for the Check-in at TBI feature."""


class EventNotFoundException(Exception):
    """Raised when a requested event does not exist, or isn't visible to the caller."""


class CheckInNotFoundException(Exception):
    """Raised when a requested check-in does not exist."""
