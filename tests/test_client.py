"""Unit tests for OpenAI client lifecycle, authentication, and error mapping."""

import os
import unittest
from openai import OpenAI
from openai.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
)


class TestOpenAIClient(unittest.TestCase):
    """Test suite covering client initialization, options, and error handling."""

    def setUp(self) -> None:
        """Configure test environment variables."""
        self.original_env = os.environ.copy()
        os.environ["OPENAI_API_KEY"] = "sk-test-mock-key"

    def tearDown(self) -> None:
        """Restore original environment variables."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_initialization(self) -> None:
        """Verify default client configuration attributes."""
        client = OpenAI(local_backend=True)
        self.assertEqual(client.base_url, "https://api.openai.com/v1")
        self.assertEqual(client.timeout, 60.0)
        self.assertEqual(client.api_key, "sk-test-mock-key")
        self.assertTrue(client.is_local)

    def test_custom_endpoint_and_organization(self) -> None:
        """Verify custom base URL and organization settings."""
        client = OpenAI(
            api_key="sk-custom-token",
            base_url="https://custom.endpoint.com/v1/",
            organization="org-12345",
            timeout=30.0,
            local_backend=True,
        )
        self.assertEqual(client.base_url, "https://custom.endpoint.com/v1")
        self.assertEqual(client.organization, "org-12345")
        self.assertEqual(client.timeout, 30.0)

    def test_context_manager_lifecycle(self) -> None:
        """Verify client behaves as a context manager."""
        with OpenAI(local_backend=True) as client:
            self.assertIsNotNone(client.chat)
            self.assertIsNotNone(client.completions)
            self.assertIsNotNone(client.embeddings)
            self.assertIsNotNone(client.models)

    def test_authentication_error_without_key_in_remote_mode(self) -> None:
        """Verify AuthenticationError is raised when remote mode lacks credentials."""
        os.environ.pop("OPENAI_API_KEY", None)
        with self.assertRaises(AuthenticationError) as ctx:
            OpenAI(api_key=None, local_backend=False)
        self.assertIn("api_key", str(ctx.exception))

    def test_http_error_code_mapping(self) -> None:
        """Verify error mapping method maps HTTP response codes to correct exception types."""
        client = OpenAI(local_backend=True)

        err_400 = client._map_http_error(400, "Invalid parameter", {"error": "bad"})
        self.assertIsInstance(err_400, BadRequestError)
        self.assertEqual(err_400.status_code, 400)

        err_401 = client._map_http_error(401, "Unauthorized", {})
        self.assertIsInstance(err_401, AuthenticationError)
        self.assertEqual(err_401.status_code, 401)

        err_404 = client._map_http_error(404, "Resource missing", {})
        self.assertIsInstance(err_404, NotFoundError)
        self.assertEqual(err_404.status_code, 404)

        err_429 = client._map_http_error(429, "Quota exceeded", {})
        self.assertIsInstance(err_429, RateLimitError)
        self.assertEqual(err_429.status_code, 429)

        err_500 = client._map_http_error(500, "Internal Server Error", {})
        self.assertIsInstance(err_500, APIError)
        self.assertEqual(err_500.status_code, 500)


if __name__ == "__main__":
    unittest.main()
