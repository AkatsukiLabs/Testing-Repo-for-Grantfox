"""Unit tests for chat completions, streaming, and parameter handling."""

import unittest
from openai import OpenAI
from openai.exceptions import BadRequestError
from openai.types import ChatCompletion, ChatCompletionChunk, ChatMessage


class TestChatCompletions(unittest.TestCase):
    """Test suite covering chat completion creation, streaming, and bounds."""

    def setUp(self) -> None:
        """Initialize local client instance."""
        self.client = OpenAI(local_backend=True)

    def test_basic_chat_completion(self) -> None:
        """Verify standard chat completion generation with system and user roles."""
        messages = [
            ChatMessage(role="system", content="You are an assistant."),
            ChatMessage(role="user", content="Who are you?"),
        ]
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        self.assertIsInstance(completion, ChatCompletion)
        self.assertEqual(completion.model, "gpt-4o")
        self.assertEqual(len(completion.choices), 1)
        self.assertEqual(completion.choices[0].message.role, "assistant")
        self.assertIn("artificial intelligence", completion.choices[0].message.content.lower())
        self.assertGreater(completion.usage.total_tokens, 0)

    def test_dict_message_inputs(self) -> None:
        """Verify message list accepts plain dictionary inputs."""
        messages = [
            {"role": "user", "content": "What is your function?"}
        ]
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        self.assertIsInstance(completion, ChatCompletion)
        self.assertEqual(completion.choices[0].finish_reason, "stop")
        self.assertIsNotNone(completion.choices[0].message.content)

    def test_max_tokens_truncation(self) -> None:
        """Verify generation terminates and assigns length reason when max_tokens is reached."""
        messages = [{"role": "user", "content": "Provide a lengthy description of natural phenomena."}]
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=2,
        )
        words = completion.choices[0].message.content.split()
        self.assertLessEqual(len(words), 2)
        self.assertEqual(completion.choices[0].finish_reason, "length")

    def test_stop_sequence_handling(self) -> None:
        """Verify generation truncates at designated stop sequences."""
        messages = [{"role": "user", "content": "Query processed: stop here please."}]
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stop=["processed"],
        )
        self.assertNotIn("processed", completion.choices[0].message.content)
        self.assertEqual(completion.choices[0].finish_reason, "stop")

    def test_empty_messages_validation(self) -> None:
        """Verify empty messages input triggers BadRequestError."""
        with self.assertRaises(BadRequestError):
            self.client.chat.completions.create(model="gpt-4o", messages=[])

    def test_streaming_chat_completion(self) -> None:
        """Verify streaming returns valid chunk events and reconstructs full message."""
        messages = [{"role": "user", "content": "Who are you?"}]
        stream = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True,
        )
        chunks = list(stream)
        self.assertGreater(len(chunks), 1)

        self.assertEqual(chunks[0].choices[0].delta.role, "assistant")

        reconstructed_tokens = []
        for chunk in chunks[1:-1]:
            self.assertIsInstance(chunk, ChatCompletionChunk)
            if chunk.choices[0].delta.content:
                reconstructed_tokens.append(chunk.choices[0].delta.content)

        final_chunk = chunks[-1]
        self.assertEqual(final_chunk.choices[0].finish_reason, "stop")

        full_streamed_text = "".join(reconstructed_tokens)
        self.assertIn("artificial intelligence", full_streamed_text.lower())


if __name__ == "__main__":
    unittest.main()
