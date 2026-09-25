"""Unit tests for model catalog listing and retrieval."""

import unittest
from openai import OpenAI
from openai.exceptions import NotFoundError
from openai.types import Model


class TestModels(unittest.TestCase):
    """Test suite covering model discovery and metadata lookup."""

    def setUp(self) -> None:
        """Initialize local client instance."""
        self.client = OpenAI(local_backend=True)

    def test_list_models_contains_standard_identifiers(self) -> None:
        """Verify model catalog contains recognized foundational model names."""
        models = self.client.models.list()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 3)

        ids = {m.id for m in models}
        self.assertIn("gpt-4o", ids)
        self.assertIn("gpt-4o-mini", ids)
        self.assertIn("text-embedding-3-small", ids)

        for model in models:
            self.assertIsInstance(model, Model)
            self.assertEqual(model.object, "model")
            self.assertGreater(model.created, 0)
            self.assertIsNotNone(model.owned_by)

    def test_retrieve_existing_model(self) -> None:
        """Verify retrieval returns valid model descriptor."""
        model = self.client.models.retrieve("gpt-4o")
        self.assertIsInstance(model, Model)
        self.assertEqual(model.id, "gpt-4o")
        self.assertEqual(model.owned_by, "system")

    def test_retrieve_unknown_model_raises_not_found(self) -> None:
        """Verify querying nonexistent model raises NotFoundError with 404 status."""
        with self.assertRaises(NotFoundError) as ctx:
            self.client.models.retrieve("non-existent-super-model")
        self.assertEqual(ctx.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
