"""Unit tests for the SimpleTokenizer module."""

import unittest
from llm.tokenizer import SimpleTokenizer


class TestSimpleTokenizer(unittest.TestCase):
    """Test suite covering tokenization, vocabulary generation, and encoding/decoding."""

    def setUp(self) -> None:
        """Initialize tokenizer and sample training texts."""
        self.tokenizer = SimpleTokenizer()
        self.sample_corpus = [
            "Hello world!",
            "Language models generate text sequentially.",
            "Hello again, world."
        ]
        self.tokenizer.build_vocab(self.sample_corpus)

    def test_special_tokens_presence(self) -> None:
        """Verify that special tokens are registered with discrete IDs."""
        self.assertEqual(self.tokenizer.pad_token_id, 0)
        self.assertEqual(self.tokenizer.unk_token_id, 1)
        self.assertEqual(self.tokenizer.bos_token_id, 2)
        self.assertEqual(self.tokenizer.eos_token_id, 3)

    def test_vocab_size_greater_than_special_tokens(self) -> None:
        """Verify vocabulary size expands past initial special tokens."""
        self.assertGreater(self.tokenizer.vocab_size, 4)

    def test_encode_with_special_tokens(self) -> None:
        """Verify encoding prepends BOS and appends EOS tokens."""
        encoded = self.tokenizer.encode("Hello world", add_special_tokens=True)
        self.assertEqual(encoded[0], self.tokenizer.bos_token_id)
        self.assertEqual(encoded[-1], self.tokenizer.eos_token_id)
        self.assertGreater(len(encoded), 2)

    def test_encode_without_special_tokens(self) -> None:
        """Verify encoding without special tokens produces raw token sequence."""
        encoded = self.tokenizer.encode("Hello world", add_special_tokens=False)
        self.assertNotIn(self.tokenizer.bos_token_id, encoded)
        self.assertNotIn(self.tokenizer.eos_token_id, encoded)
        self.assertEqual(len(encoded), 2)

    def test_unknown_token_mapping(self) -> None:
        """Verify out-of-vocabulary words map to unk token ID."""
        encoded = self.tokenizer.encode("supercalifragilistic", add_special_tokens=False)
        self.assertEqual(encoded, [self.tokenizer.unk_token_id])

    def test_roundtrip_encode_decode(self) -> None:
        """Verify text encoding and subsequent decoding preserves word tokens."""
        text = "hello world"
        encoded = self.tokenizer.encode(text, add_special_tokens=False)
        decoded = self.tokenizer.decode(encoded, skip_special_tokens=True)
        self.assertEqual(decoded, text)

    def test_empty_string_handling(self) -> None:
        """Verify empty string produces empty token list without special tokens."""
        encoded = self.tokenizer.encode("", add_special_tokens=False)
        self.assertEqual(encoded, [])


if __name__ == "__main__":
    unittest.main()
