"""Unit tests for embedding generation, vector normalization, and semantic similarity."""

import math
import unittest
from openai import OpenAI
from openai.exceptions import BadRequestError
from openai.types import EmbeddingResponse


class TestEmbeddings(unittest.TestCase):
    """Test suite covering embedding vector calculations and dimensional consistency."""

    def setUp(self) -> None:
        """Initialize local client instance."""
        self.client = OpenAI(local_backend=True)

    def _cosine_similarity(self, vec_a: list, vec_b: list) -> float:
        """Compute cosine similarity between two float vectors."""
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def test_single_embedding_shape_and_norm(self) -> None:
        """Verify embedding has correct dimensions and unit Euclidean norm."""
        response = self.client.embeddings.create(
            input="artificial intelligence and neural architectures",
            model="text-embedding-3-small",
            dimensions=64,
        )
        self.assertIsInstance(response, EmbeddingResponse)
        self.assertEqual(len(response.data), 1)

        vector = response.data[0].embedding
        self.assertEqual(len(vector), 64)

        l2_norm = math.sqrt(sum(x * x for x in vector))
        self.assertAlmostEqual(l2_norm, 1.0, places=4)
        self.assertGreater(response.usage.total_tokens, 0)

    def test_batch_embeddings(self) -> None:
        """Verify batch inputs produce matching quantity of indexed embeddings."""
        inputs = ["first document", "second document", "third document"]
        response = self.client.embeddings.create(
            input=inputs,
            model="text-embedding-3-small",
            dimensions=32,
        )
        self.assertEqual(len(response.data), 3)
        for i, item in enumerate(response.data):
            self.assertEqual(item.index, i)
            self.assertEqual(len(item.embedding), 32)
            l2_norm = math.sqrt(sum(x * x for x in item.embedding))
            self.assertAlmostEqual(l2_norm, 1.0, places=4)

    def test_semantic_similarity_contrast(self) -> None:
        """Verify that related texts exhibit higher cosine similarity than unrelated texts."""
        resp_ml_1 = self.client.embeddings.create(
            input="machine learning neural networks deep learning",
            dimensions=64,
        )
        resp_ml_2 = self.client.embeddings.create(
            input="deep neural network learning architectures",
            dimensions=64,
        )
        resp_cooking = self.client.embeddings.create(
            input="boiling tomato pasta sauce garlic oregano dinner",
            dimensions=64,
        )

        sim_related = self._cosine_similarity(
            resp_ml_1.data[0].embedding,
            resp_ml_2.data[0].embedding,
        )
        sim_unrelated = self._cosine_similarity(
            resp_ml_1.data[0].embedding,
            resp_cooking.data[0].embedding,
        )

        self.assertGreater(sim_related, sim_unrelated)

    def test_invalid_dimensions_error(self) -> None:
        """Verify negative or zero dimension raises BadRequestError."""
        with self.assertRaises(BadRequestError):
            self.client.embeddings.create(input="test phrase", dimensions=0)


if __name__ == "__main__":
    unittest.main()
