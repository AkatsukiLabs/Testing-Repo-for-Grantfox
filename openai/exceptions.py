"""Exceptions raised by the OpenAI package."""

from typing import Any, Optional


class OpenAIError(Exception):
    """Base exception for all errors raised by the OpenAI client."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[Any] = None) -> None:
        """Initialize OpenAIError with optional status code and response payload.

        Args:
            message: Descriptive error message.
            status_code: HTTP response status code if available.
            response_body: Raw response payload if available.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        """Return formatted string representation of the exception."""
        if self.status_code is not None:
            return f"[{self.status_code}] {self.message}"
        return self.message


class APIError(OpenAIError):
    """Exception raised when an API endpoint returns an unhandled error."""
    pass


class AuthenticationError(OpenAIError):
    """Exception raised when authentication credentials are missing or rejected."""
    pass


class BadRequestError(OpenAIError):
    """Exception raised when a request payload fails validation."""
    pass


class NotFoundError(OpenAIError):
    """Exception raised when a requested resource does not exist."""
    pass


class RateLimitError(OpenAIError):
    """Exception raised when client requests exceed quota or throughput limits."""
    pass


class APIConnectionError(OpenAIError):
    """Exception raised when network transport fails to connect to the upstream server."""
    pass
