"""Unit tests for SpaceX rocket fleet data models and queries."""

import unittest

from spacex import Rocket, SpaceX


class TestRockets(unittest.TestCase):
    """Test suite for rockets resource catalog and vehicle specifications."""

    def setUp(self) -> None:
        """Initialize client before test execution."""
        self.client = SpaceX()

    def test_list_all_rockets(self) -> None:
        """Verify complete rocket roster is retrievable."""
        rockets = self.client.rockets.list()
        self.assertGreaterEqual(len(rockets), 4)
        names = [r.name for r in rockets]
        self.assertIn("Falcon 1", names)
        self.assertIn("Falcon 9", names)
        self.assertIn("Falcon Heavy", names)
        self.assertIn("Starship", names)

    def test_get_falcon_9_specifications(self) -> None:
        """Verify detailed technical specifications of Falcon 9."""
        f9 = self.client.rockets.get("5e9d0d95eda69973a809d1ec")
        self.assertEqual(f9.name, "Falcon 9")
        self.assertTrue(f9.active)
        self.assertEqual(f9.stages, 2)
        self.assertEqual(f9.boosters, 0)
        self.assertEqual(f9.engines.number, 9)
        self.assertEqual(f9.engines.type, "merlin")
        self.assertEqual(f9.engines.version, "1D+")
        self.assertEqual(f9.first_stage.engines, 9)
        self.assertTrue(f9.first_stage.reusable)
        self.assertEqual(f9.mass.kg, 549054)
        self.assertEqual(f9.height.meters, 70.0)

    def test_get_starship_specifications(self) -> None:
        """Verify Super Heavy and Starship propulsion specifications."""
        starship = self.client.rockets.get("5e9d0d96eda699382d09d1ee")
        self.assertEqual(starship.name, "Starship")
        self.assertTrue(starship.active)
        self.assertEqual(starship.engines.number, 33)
        self.assertEqual(starship.engines.type, "raptor")
        self.assertEqual(starship.engines.propellant_2, "liquid methane")
        self.assertTrue(starship.first_stage.reusable)
        self.assertTrue(starship.second_stage.reusable)
        self.assertEqual(starship.height.meters, 121.0)
        self.assertEqual(starship.mass.kg, 5000000)

    def test_query_active_rockets(self) -> None:
        """Verify query filtering by vehicle operational status."""
        result = self.client.rockets.query(query={"active": True})
        self.assertEqual(result.total_docs, 3)
        for r in result.docs:
            self.assertTrue(r.active)

    def test_query_inactive_rockets(self) -> None:
        """Verify query returns decommissioned vehicles."""
        result = self.client.rockets.query(query={"active": False})
        self.assertEqual(result.total_docs, 1)
        self.assertEqual(result.docs[0].name, "Falcon 1")

    def test_rocket_serialization_cycle(self) -> None:
        """Verify lossless dictionary serialization and deserialization."""
        f9 = self.client.rockets.get("5e9d0d95eda69973a809d1ec")
        raw_dict = f9.to_dict()
        reconstituted = Rocket.from_dict(raw_dict)
        self.assertEqual(f9.id, reconstituted.id)
        self.assertEqual(f9.name, reconstituted.name)
        self.assertEqual(f9.engines.thrust_sea_level.kN, reconstituted.engines.thrust_sea_level.kN)


if __name__ == "__main__":
    unittest.main()
