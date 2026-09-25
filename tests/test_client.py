"""Unit tests for SpaceX client configuration and lifecycle."""

import unittest

from spacex import (
    NotFoundError,
    SpaceX,
    SpaceXClient,
    ValidationError,
)


class TestSpaceXClient(unittest.TestCase):
    """Test suite for client initialization, configuration, and base methods."""

    def test_client_initialization_defaults(self) -> None:
        """Verify client initializes with sensible defaults in offline mode."""
        client = SpaceX()
        self.assertEqual(client.base_url, "https://api.spacexdata.com/v4")
        self.assertTrue(client.offline)
        self.assertEqual(client.timeout, 15.0)

    def test_client_custom_configuration(self) -> None:
        """Verify custom parameters are preserved on instantiation."""
        client = SpaceX(
            base_url="https://custom-mirror.spacex.org/v4/",
            offline=False,
            timeout=30.0,
        )
        self.assertEqual(client.base_url, "https://custom-mirror.spacex.org/v4")
        self.assertFalse(client.offline)
        self.assertEqual(client.timeout, 30.0)

    def test_client_class_alias(self) -> None:
        """Ensure SpaceXClient is an identical alias for SpaceX."""
        self.assertIs(SpaceXClient, SpaceX)

    def test_context_manager_protocol(self) -> None:
        """Verify context manager enters and exits cleanly."""
        with SpaceX() as client:
            self.assertIsInstance(client, SpaceX)
            company = client.company.get()
            self.assertEqual(company.name, "SpaceX")
            self.assertEqual(company.founder, "Elon Musk")
            self.assertEqual(company.founded, 2002)

    def test_not_found_error_raising(self) -> None:
        """Verify NotFoundError is raised with specific resource ID."""
        client = SpaceX()
        with self.assertRaises(NotFoundError) as ctx:
            client.rockets.get("non-existent-rocket-id-12345")
        self.assertEqual(ctx.exception.resource_id, "non-existent-rocket-id-12345")

    def test_validation_error_on_invalid_collection(self) -> None:
        """Verify ValidationError occurs on invalid internal collection lookup."""
        client = SpaceX()
        with self.assertRaises(ValidationError):
            client.engine.get_collection("invalid_collection_name")


if __name__ == "__main__":
    unittest.main()
