"""Core client class for the OpenAI API and local inference engine."""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Iterator, Optional

from openai.engine import LocalEngine
from openai.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    OpenAIError,
    RateLimitError,
)
from openai.resources.chat import Chat
from openai.resources.completions import Completions
from openai.resources.embeddings import Embeddings
from openai.resources.models import Models
from openai.types import ChatCompletionChunk


class OpenAI:
    """Client for interacting with OpenAI endpoints and offline local engine."""

    DEFAULT_BASE_URL: str = "https://api.openai.com/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 2,
        local_backend: bool = True,
    ) -> None:
        """Initialize OpenAI client.

        Args:
            api_key: OpenAI API key string. Defaults to OPENAI_API_KEY environment variable.
            base_url: Base endpoint URL. Defaults to https://api.openai.com/v1.
            organization: Organization identifier. Defaults to OPENAI_ORG_ID environment variable.
            timeout: Request timeout in seconds.
            max_retries: Number of retry attempts on network failures.
            local_backend: When True, queries execute locally without network transmission.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or self.DEFAULT_BASE_URL).rstrip("/")
        self.organization = organization or os.environ.get("OPENAI_ORG_ID")
        self.timeout = timeout
        self.max_retries = max_retries
        self.is_local = local_backend

        if not self.is_local and not self.api_key:
            raise AuthenticationError(
                "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable."
            )

        self.engine = LocalEngine()
        self.chat = Chat(self)
        self.completions = Completions(self)
        self.embeddings = Embeddings(self)
        self.models = Models(self)

    def __enter__(self) -> "OpenAI":
        """Enter context manager scope."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager scope."""
        self.close()

    def close(self) -> None:
        """Release any open client resources."""
        pass

    def _build_headers(self) -> Dict[str, str]:
        """Construct standard HTTP authorization and content headers."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "OpenAI-Python-Client/1.0.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        return headers

    def _map_http_error(self, code: int, message: str, body: Any) -> OpenAIError:
        """Map HTTP response status codes to specific OpenAI exception types."""
        if code in (401, 403):
            return AuthenticationError(message, status_code=code, response_body=body)
        elif code == 400:
            return BadRequestError(message, status_code=code, response_body=body)
        elif code == 404:
            return NotFoundError(message, status_code=code, response_body=body)
        elif code == 429:
            return RateLimitError(message, status_code=code, response_body=body)
        elif code >= 500:
            return APIError(message, status_code=code, response_body=body)
        return APIError(message, status_code=code, response_body=body)

    def request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send synchronous HTTP request to upstream OpenAI endpoint.

        Args:
            method: HTTP method verb (GET, POST, DELETE).
            path: Target endpoint path.
            json_data: Payload body to serialize as JSON.

        Returns:
            Parsed JSON dictionary response.
        """
        url = f"{self.base_url}{path}"
        headers = self._build_headers()
        body_bytes = json.dumps(json_data).encode("utf-8") if json_data is not None else None

        req = urllib.request.Request(url=url, data=body_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content = response.read().decode("utf-8")
                return json.loads(content)
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8")
            try:
                parsed_err = json.loads(err_body)
                err_message = parsed_err.get("error", {}).get("message", err_body)
            except Exception:
                err_message = err_body or str(err)
            raise self._map_http_error(err.code, err_message, err_body) from err
        except urllib.error.URLError as err:
            raise APIConnectionError(f"Failed to connect to OpenAI API at {url}: {err.reason}") from err

    def request_stream(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Iterator[ChatCompletionChunk]:
        """Send streaming request and yield server-sent event completion chunks.

        Args:
            method: HTTP method verb (POST).
            path: Target endpoint path.
            json_data: Payload body.

        Returns:
            Generator yielding parsed ChatCompletionChunk instances.
        """
        url = f"{self.base_url}{path}"
        headers = self._build_headers()
        headers["Accept"] = "text/event-stream"
        body_bytes = json.dumps(json_data).encode("utf-8") if json_data is not None else None

        req = urllib.request.Request(url=url, data=body_bytes, headers=headers, method=method)

        try:
            response = urllib.request.urlopen(req, timeout=self.timeout)
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8")
            raise self._map_http_error(err.code, err_body, err_body) from err
        except urllib.error.URLError as err:
            raise APIConnectionError(f"Connection failed to {url}: {err.reason}") from err

        with response:
            for line in response:
                decoded_line = line.decode("utf-8").strip()
                if not decoded_line or not decoded_line.startswith("data: "):
                    continue
                data_str = decoded_line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    payload = json.loads(data_str)
                    yield ChatCompletionChunk.from_dict(payload)
                except json.JSONDecodeError:
                    continue
