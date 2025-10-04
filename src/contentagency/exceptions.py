"""
Custom exceptions for ContentAgency.
"""


class ValidationError(Exception):
    """Raised when input data validation fails."""
    pass


class DataFormatError(Exception):
    """Raised when data format is invalid or malformed."""
    pass
