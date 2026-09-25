"""Autoregressive language model implementation with sampling and perplexity computation."""

import math
import random
from collections import defaultdict, Counter
from typing import List, Dict, Optional, Tuple
from .tokenizer import SimpleTokenizer


class LanguageModel:
    """An autoregressive n-gram language model supporting temperature, top-k, and repetition penalties."""

    def __init__(
        self,
        tokenizer: Optional[SimpleTokenizer] = None,
        context_window: int = 3,
        smoothing: float = 0.1,
    ) -> None:
        """Initialize the language model with tokenizer, context length, and Laplace smoothing factor."""
        self.tokenizer: SimpleTokenizer = tokenizer if tokenizer is not None else SimpleTokenizer()
        self.context_window: int = max(1, context_window)
        self.smoothing: float = max(1e-5, smoothing)
        self.transitions: Dict[Tuple[int, ...], Counter] = defaultdict(Counter)
        self.unigram_counts: Counter = Counter()
        self.total_tokens: int = 0

    def fit(self, texts: List[str]) -> None:
        """Train transition distributions on input training texts."""
        self.tokenizer.build_vocab(texts)
        self.transitions.clear()
        self.unigram_counts.clear()
        self.total_tokens = 0

        for text in texts:
            encoded = self.tokenizer.encode(text, add_special_tokens=True)
            for idx, token_id in enumerate(encoded):
                self.unigram_counts[token_id] += 1
                self.total_tokens += 1
                for window_size in range(1, self.context_window + 1):
                    if idx >= window_size:
                        context = tuple(encoded[idx - window_size : idx])
                        self.transitions[context][token_id] += 1

    def compute_logits(self, context_ids: List[int]) -> Dict[int, float]:
        """Compute smoothed log-probabilities for all vocabulary tokens given context token IDs."""
        vocab_size = self.tokenizer.vocab_size
        logits: Dict[int, float] = {}

        selected_counts = Counter()
        for window_size in range(min(len(context_ids), self.context_window), 0, -1):
            sub_context = tuple(context_ids[-window_size:])
            if sub_context in self.transitions:
                selected_counts = self.transitions[sub_context]
                break

        context_total = sum(selected_counts.values())
        denominator = context_total + (self.smoothing * vocab_size)

        for token_id in range(vocab_size):
            count = selected_counts[token_id]
            if count == 0 and self.unigram_counts[token_id] > 0:
                base_prob = self.unigram_counts[token_id] / max(1, self.total_tokens)
                prob = (self.smoothing * base_prob) / denominator
            else:
                prob = (count + self.smoothing) / denominator
            logits[token_id] = math.log(max(prob, 1e-12))

        return logits

    def _apply_sampling_controls(
        self,
        logits: Dict[int, float],
        temperature: float,
        top_k: int,
        repetition_penalty: float,
        generated_tokens: List[int],
    ) -> List[Tuple[int, float]]:
        """Apply repetition penalty, temperature scaling, and top-k filtering to logits."""
        scaled_logits: Dict[int, float] = {}
        penalty = max(1.0, repetition_penalty)
        temp = max(1e-4, temperature)

        for token_id, logit in logits.items():
            current_logit = logit
            if token_id in generated_tokens and penalty > 1.0:
                if current_logit > 0:
                    current_logit /= penalty
                else:
                    current_logit *= penalty
            scaled_logits[token_id] = current_logit / temp

        sorted_items = sorted(scaled_logits.items(), key=lambda x: x[1], reverse=True)

        if 0 < top_k < len(sorted_items):
            sorted_items = sorted_items[:top_k]

        max_logit = sorted_items[0][1]
        exp_values = [(token_id, math.exp(logit - max_logit)) for token_id, logit in sorted_items]
        sum_exp = sum(val for _, val in exp_values)

        return [(token_id, val / sum_exp) for token_id, val in exp_values]

    def sample_next_token(
        self,
        context_ids: List[int],
        temperature: float = 1.0,
        top_k: int = 0,
        repetition_penalty: float = 1.0,
        generated_history: Optional[List[int]] = None,
        seed: Optional[int] = None,
    ) -> int:
        """Sample the next token ID from conditioned probability distribution."""
        if seed is not None:
            random.seed(seed)

        logits = self.compute_logits(context_ids)
        history = generated_history if generated_history is not None else []
        probabilities = self._apply_sampling_controls(
            logits=logits,
            temperature=temperature,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            generated_tokens=history,
        )

        tokens = [token_id for token_id, _ in probabilities]
        weights = [prob for _, prob in probabilities]
        return random.choices(tokens, weights=weights, k=1)[0]

    def generate(
        self,
        prompt: str,
        max_tokens: int = 32,
        temperature: float = 1.0,
        top_k: int = 0,
        repetition_penalty: float = 1.0,
        seed: Optional[int] = None,
    ) -> str:
        """Autoregressively generate text continuations given a prompt."""
        if seed is not None:
            random.seed(seed)

        encoded = self.tokenizer.encode(prompt, add_special_tokens=False)
        context = [self.tokenizer.bos_token_id] + encoded
        generated: List[int] = []

        for _ in range(max_tokens):
            next_token = self.sample_next_token(
                context_ids=context,
                temperature=temperature,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
                generated_history=generated,
            )
            if next_token == self.tokenizer.eos_token_id:
                break
            generated.append(next_token)
            context.append(next_token)

        return self.tokenizer.decode(generated, skip_special_tokens=True)

    def compute_perplexity(self, text: str) -> float:
        """Calculate model perplexity on an input test string."""
        encoded = self.tokenizer.encode(text, add_special_tokens=True)
        if len(encoded) < 2:
            return 1.0

        total_neg_log_likelihood: float = 0.0
        n_predictions: int = 0

        for idx in range(1, len(encoded)):
            context = encoded[:idx]
            target_token = encoded[idx]
            logits = self.compute_logits(context)

            max_logit = max(logits.values())
            sum_exp = sum(math.exp(val - max_logit) for val in logits.values())
            log_prob = (logits[target_token] - max_logit) - math.log(sum_exp)

            total_neg_log_likelihood -= log_prob
            n_predictions += 1

        if n_predictions == 0:
            return 1.0

        mean_nll = total_neg_log_likelihood / n_predictions
        return math.exp(mean_nll)
