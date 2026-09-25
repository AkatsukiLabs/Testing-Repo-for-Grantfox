"""Unit tests for SpaceX launches, flight manifests, and relational queries."""

import unittest

from spacex import Launch, SpaceX


class TestLaunches(unittest.TestCase):
    """Test suite for launch events, historical records, and mission queries."""

    def setUp(self) -> None:
        """Initialize client before test execution."""
        self.client = SpaceX()

    def test_list_all_launches(self) -> None:
        """Verify listing all launches returns complete manifest."""
        launches = self.client.launches.list()
        self.assertGreaterEqual(len(launches), 7)

    def test_get_launch_by_id(self) -> None:
        """Verify retrieving specific launch by unique ID."""
        launch = self.client.launches.get("5eb87d46ffd86e000604b388")
        self.assertEqual(launch.name, "CCtCap Demo Mission 2")
        self.assertEqual(launch.flight_number, 94)
        self.assertTrue(launch.success)
        self.assertFalse(launch.upcoming)
        self.assertEqual(len(launch.crew), 2)
        self.assertIn("5ebf1a6e23a9a60006e03a7a", launch.crew)

    def test_latest_launch(self) -> None:
        """Verify latest launch returns the most recent completed flight."""
        latest = self.client.launches.latest()
        self.assertEqual(latest.flight_number, 200)
        self.assertEqual(latest.name, "Starship Flight 5")
        self.assertFalse(latest.upcoming)

    def test_next_launch(self) -> None:
        """Verify next launch returns closest scheduled future flight."""
        next_launch = self.client.launches.next()
        self.assertEqual(next_launch.flight_number, 201)
        self.assertEqual(next_launch.name, "Starlink Group 6-50")
        self.assertTrue(next_launch.upcoming)

    def test_upcoming_and_past_partition(self) -> None:
        """Verify partition between past missions and upcoming schedules."""
        upcoming = self.client.launches.upcoming()
        past = self.client.launches.past()
        self.assertTrue(all(l.upcoming for l in upcoming))
        self.assertTrue(all(not l.upcoming for l in past))
        total = len(upcoming) + len(past)
        self.assertEqual(total, len(self.client.launches.list()))

    def test_query_filter_by_success(self) -> None:
        """Verify filtering launches by success status."""
        successful = self.client.launches.query(query={"success": True})
        self.assertGreaterEqual(successful.total_docs, 5)
        for doc in successful.docs:
            self.assertTrue(doc.success)

        failed = self.client.launches.query(query={"success": False})
        self.assertEqual(failed.total_docs, 1)
        self.assertEqual(failed.docs[0].flight_number, 1)
        self.assertGreater(len(failed.docs[0].failures), 0)

    def test_query_populate_rocket_and_launchpad(self) -> None:
        """Verify relational expansion of foreign keys in query results."""
        result = self.client.launches.query(
            query={"flight_number": 94},
            options={"populate": ["rocket", "launchpad", "crew"]},
        )
        self.assertEqual(len(result.docs), 1)
        launch = result.docs[0]
        self.assertIsInstance(launch.rocket, dict)
        self.assertEqual(launch.rocket.get("name"), "Falcon 9")
        self.assertIsInstance(launch.launchpad, dict)
        self.assertEqual(launch.launchpad.get("name"), "LC-39A")
        self.assertEqual(len(launch.crew), 2)
        self.assertIsInstance(launch.crew[0], dict)
        self.assertEqual(launch.crew[0].get("name"), "Robert Behnken")

    def test_launch_core_telemetry_and_recovery(self) -> None:
        """Verify recovery mode details on Falcon 9 landing."""
        launch = self.client.launches.get("5eb87d03ffd86e000604b350")
        self.assertEqual(len(launch.cores), 1)
        core = launch.cores[0]
        self.assertTrue(core.gridfins)
        self.assertTrue(core.legs)
        self.assertTrue(core.landing_attempt)
        self.assertTrue(core.landing_success)
        self.assertEqual(core.landing_type, "RTLS")


if __name__ == "__main__":
    unittest.main()
