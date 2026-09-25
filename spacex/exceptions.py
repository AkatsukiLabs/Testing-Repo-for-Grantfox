"""Exception hierarchy for SpaceX API client operations."""

from typing import Any, Optional


class SpaceXError(Exception):
    """Base exception for all SpaceX API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        if self.status_code is not None:
            return f"[{self.status_code}] {self.message}"
        return self.message


class NotFoundError(SpaceXError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_id: Optional[str] = None,
        status_code: int = 404,
    ) -> None:
        super().__init__(message, status_code=status_code)
        self.resource_id = resource_id


class ValidationError(SpaceXError):
    """Raised when query or request arguments fail validation constraints."""

    def __init__(
        self,
        message: str = "Validation error",
        status_code: int = 400,
        errors: Optional[list] = None,
    ) -> None:
        super().__init__(message, status_code=status_code)
        self.errors = errors or []


class APIConnectionError(SpaceXError):
    """Raised when an HTTP connection to the remote SpaceX API fails."""

    def __init__(self, message: str = "Failed to connect to SpaceX API") -> None:
        super().__init__(message, status_code=None)


class RateLimitError(SpaceXError):
    """Raised when the SpaceX API returns an HTTP 429 Too Many Requests response."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int = 429,
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, status_code=status_code)
        self.retry_after = retry_after
