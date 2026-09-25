"""Unit tests for tool definitions and function call detection."""

import json
import unittest
from openai import OpenAI
from openai.types import ChatCompletion


class TestToolCalling(unittest.TestCase):
    """Test suite covering function calling and tool invocation detection."""

    def setUp(self) -> None:
        """Initialize local client instance and sample tool specifications."""
        self.client = OpenAI(local_backend=True)
        self.weather_tool = {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City and state"},
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }

    def test_tool_call_invocation(self) -> None:
        """Verify matching user prompt triggers function tool call with finish_reason tool_calls."""
        messages = [
            {"role": "user", "content": "What is the weather in Tokyo? get_current_weather please."}
        ]
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=[self.weather_tool],
        )
        self.assertIsInstance(completion, ChatCompletion)
        choice = completion.choices[0]
        self.assertEqual(choice.finish_reason, "tool_calls")
        self.assertIsNotNone(choice.message.tool_calls)
        self.assertEqual(len(choice.message.tool_calls), 1)

        tool_call = choice.message.tool_calls[0]
        self.assertEqual(tool_call.type, "function")
        self.assertEqual(tool_call.function.name, "get_current_weather")

        args = json.loads(tool_call.function.arguments)
        self.assertIn("location", args)

    def test_tool_choice_none_suppresses_calls(self) -> None:
        """Verify tool_choice set to none forces standard textual output."""
        messages = [
            {"role": "user", "content": "What is the weather in Tokyo? get_current_weather please."}
        ]
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=[self.weather_tool],
            tool_choice="none",
        )
        choice = completion.choices[0]
        self.assertEqual(choice.finish_reason, "stop")
        self.assertIsNone(choice.message.tool_calls)
        self.assertIsNotNone(choice.message.content)

    def test_tool_choice_explicit_function(self) -> None:
        """Verify tool_choice targeting explicit function name guarantees invocation."""
        messages = [{"role": "user", "content": "Greetings!"}]
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=[self.weather_tool],
            tool_choice={"type": "function", "function": {"name": "get_current_weather"}},
        )
        choice = completion.choices[0]
        self.assertEqual(choice.finish_reason, "tool_calls")
        self.assertEqual(choice.message.tool_calls[0].function.name, "get_current_weather")


if __name__ == "__main__":
    unittest.main()
