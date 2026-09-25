"""Unit tests for the LanguageModel class."""

import unittest
from llm.tokenizer import SimpleTokenizer
from llm.model import LanguageModel


class TestLanguageModel(unittest.TestCase):
    """Test suite covering model training, logit computations, autoregressive generation, and perplexity."""

    def setUp(self) -> None:
        """Initialize language model with sample training corpus."""
        self.tokenizer = SimpleTokenizer()
        self.model = LanguageModel(tokenizer=self.tokenizer, context_window=2, smoothing=0.1)
        self.training_corpus = [
            "the quick brown fox jumps over the lazy dog",
            "the lazy dog slept under the tree",
            "the quick brown fox loves running"
        ]
        self.model.fit(self.training_corpus)

    def test_transitions_populated_after_fit(self) -> None:
        """Verify model transitions are recorded from corpus."""
        self.assertGreater(len(self.model.transitions), 0)
        self.assertGreater(self.model.total_tokens, 0)

    def test_compute_logits_validity(self) -> None:
        """Verify computed logits match vocabulary size and contain valid real numbers."""
        encoded_prompt = self.tokenizer.encode("the quick", add_special_tokens=False)
        logits = self.model.compute_logits(encoded_prompt)
        self.assertEqual(len(logits), self.tokenizer.vocab_size)
        for token_id, logit in logits.items():
            self.assertIsInstance(logit, float)
            self.assertFalse(float("-inf") == logit)
            self.assertFalse(float("inf") == logit)

    def test_deterministic_generation_with_seed(self) -> None:
        """Verify generation with identical seeds produces identical outputs."""
        output_1 = self.model.generate(prompt="the quick", max_tokens=6, seed=42)
        output_2 = self.model.generate(prompt="the quick", max_tokens=6, seed=42)
        self.assertEqual(output_1, output_2)
        self.assertIsInstance(output_1, str)

    def test_max_tokens_constraint(self) -> None:
        """Verify generation does not exceed requested maximum token budget."""
        output = self.model.generate(prompt="the", max_tokens=4, seed=123)
        tokens = self.tokenizer.encode(output, add_special_tokens=False)
        self.assertLessEqual(len(tokens), 4)

    def test_compute_perplexity_finite_positive(self) -> None:
        """Verify perplexity on training and novel sequences returns finite positive value."""
        perp_train = self.model.compute_perplexity("the quick brown fox")
        self.assertGreater(perp_train, 0.0)
        self.assertLess(perp_train, 10000.0)

    def test_sampling_controls_top_k(self) -> None:
        """Verify top_k parameter restricts sampling candidate pool."""
        encoded = self.tokenizer.encode("the", add_special_tokens=False)
        logits = self.model.compute_logits(encoded)
        filtered = self.model._apply_sampling_controls(
            logits=logits,
            temperature=1.0,
            top_k=2,
            repetition_penalty=1.0,
            generated_tokens=[],
        )
        self.assertEqual(len(filtered), 2)
        self.assertAlmostEqual(sum(prob for _, prob in filtered), 1.0, places=5)


if __name__ == "__main__":
    unittest.main()
