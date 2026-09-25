"""Unit tests for SpaceX capsules, Dragon spacecraft, and crew members."""

import unittest

from spacex import Capsule, CrewMember, SpaceX


class TestCapsulesAndCrew(unittest.TestCase):
    """Test suite for human spaceflight crew and capsule pressure vessel assets."""

    def setUp(self) -> None:
        """Initialize client before test execution."""
        self.client = SpaceX()

    def test_list_all_capsules(self) -> None:
        """Verify listing all capsules returns fleet roster."""
        capsules = self.client.capsules.list()
        self.assertGreaterEqual(len(capsules), 3)
        serials = [c.serial for c in capsules]
        self.assertIn("C101", serials)
        self.assertIn("C206", serials)
        self.assertIn("C207", serials)

    def test_get_capsule_details(self) -> None:
        """Verify detailed attributes of Endeavour capsule C206."""
        capsule = self.client.capsules.get("5e9e2c5df359188bfb3b2675")
        self.assertEqual(capsule.serial, "C206")
        self.assertEqual(capsule.status, "active")
        self.assertEqual(capsule.type, "Dragon 2.0")
        self.assertGreaterEqual(capsule.reuse_count, 4)
        self.assertGreaterEqual(capsule.water_landings, 5)

    def test_query_active_capsules(self) -> None:
        """Verify filtering capsules by active status."""
        result = self.client.capsules.query(query={"status": "active"})
        self.assertEqual(result.total_docs, 2)
        for c in result.docs:
            self.assertEqual(c.status, "active")

    def test_list_all_crew_members(self) -> None:
        """Verify listing all crew members."""
        crew = self.client.crew.list()
        self.assertGreaterEqual(len(crew), 4)
        names = [m.name for m in crew]
        self.assertIn("Robert Behnken", names)
        self.assertIn("Douglas Hurley", names)
        self.assertIn("Jared Isaacman", names)

    def test_get_crew_member_details(self) -> None:
        """Verify specific crew member fields and flight assignments."""
        behnken = self.client.crew.get("5ebf1a6e23a9a60006e03a7a")
        self.assertEqual(behnken.name, "Robert Behnken")
        self.assertEqual(behnken.agency, "NASA")
        self.assertEqual(behnken.status, "retired")
        self.assertIn("5eb87d46ffd86e000604b388", behnken.launches)

    def test_crew_serialization(self) -> None:
        """Verify serialization and deserialization of crew model."""
        isaacman = self.client.crew.get("607a37545a9634000662d558")
        data = isaacman.to_dict()
        reconstructed = CrewMember.from_dict(data)
        self.assertEqual(isaacman.id, reconstructed.id)
        self.assertEqual(isaacman.name, reconstructed.name)
        self.assertEqual(isaacman.status, reconstructed.status)


if __name__ == "__main__":
    unittest.main()
