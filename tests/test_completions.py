"""Unit tests for legacy completions resource endpoint."""

import unittest
from openai import OpenAI
from openai.types import Completion


class TestCompletions(unittest.TestCase):
    """Test suite covering prompt completions and token limits."""

    def setUp(self) -> None:
        """Initialize local client instance."""
        self.client = OpenAI(local_backend=True)

    def test_basic_completion(self) -> None:
        """Verify prompt generation produces completion text and usage metrics."""
        response = self.client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt="Once upon a time",
            max_tokens=10,
        )
        self.assertIsInstance(response, Completion)
        self.assertEqual(len(response.choices), 1)
        self.assertIn("Once upon a time", response.choices[0].text)
        self.assertGreater(response.usage.total_tokens, 0)

    def test_completion_stop_sequence(self) -> None:
        """Verify completion halts before requested stop substring."""
        response = self.client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt="Alpha beta gamma delta",
            stop=["continuation"],
        )
        self.assertNotIn("continuation", response.choices[0].text)
        self.assertEqual(response.choices[0].finish_reason, "stop")


if __name__ == "__main__":
    unittest.main()
