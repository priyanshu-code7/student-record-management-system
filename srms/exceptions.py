"""Custom exceptions used across the Student Record Management System."""


class SRMSError(Exception):
    """Base class for all application errors."""


class ValidationError(SRMSError):
    """Raised when user input is invalid."""


class DuplicateRecordError(SRMSError):
    """Raised when a roll number or email already exists."""


class RecordNotFoundError(SRMSError):
    """Raised when a student record cannot be found."""


class DatabaseError(SRMSError):
    """Raised when a database operation fails."""
