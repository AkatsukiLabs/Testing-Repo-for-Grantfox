"""Unit tests for recovery ships, payloads, launchpads, and Starlink records."""

import unittest

from spacex import Payload, Ship, SpaceX


class TestShipsPayloadsLaunchpads(unittest.TestCase):
    """Test suite for maritime recovery fleet, satellite payloads, and launchpads."""

    def setUp(self) -> None:
        """Initialize client before test execution."""
        self.client = SpaceX()

    def test_list_all_ships(self) -> None:
        """Verify maritime vessel catalog returns recovery fleet."""
        ships = self.client.ships.list()
        self.assertGreaterEqual(len(ships), 2)
        names = [s.name for s in ships]
        self.assertIn("Of Course I Still Love You", names)
        self.assertIn("Just Read The Instructions", names)

    def test_get_ship_specifications(self) -> None:
        """Verify ASDS droneship attributes."""
        ocisly = self.client.ships.get("5ea6ed2e080df40006979607")
        self.assertEqual(ocisly.name, "Of Course I Still Love You")
        self.assertTrue(ocisly.active)
        self.assertIn("Droneship", ocisly.roles)
        self.assertEqual(ocisly.type, "Barge")

    def test_list_payloads(self) -> None:
        """Verify satellite and cargo payloads catalog."""
        payloads = self.client.payloads.list()
        self.assertGreaterEqual(len(payloads), 5)
        names = [p.name for p in payloads]
        self.assertIn("FalconSat", names)
        self.assertIn("Tesla Roadster", names)
        self.assertIn("Crew Dragon DM-2", names)

    def test_get_tesla_roadster_payload(self) -> None:
        """Verify heliocentric orbit payload characteristics."""
        roadster = self.client.payloads.get("5eb0e4bdb6c3bb0006eeb1eb")
        self.assertEqual(roadster.name, "Tesla Roadster")
        self.assertEqual(roadster.orbit, "HCO")
        self.assertEqual(roadster.regime, "solar")
        self.assertGreater(roadster.semi_major_axis_km, 100000000.0)

    def test_starlink_telemetry(self) -> None:
        """Verify Starlink orbital element records."""
        satellites = self.client.starlink.list()
        self.assertGreaterEqual(len(satellites), 1)
        node = self.client.starlink.get("5eed770f096e59000698560d")
        self.assertEqual(node.norad_id, 44713)
        self.assertEqual(node.version, "v1.5")
        self.assertAlmostEqual(node.inclination_deg, 53.22, places=2)

    def test_launchpads_catalog(self) -> None:
        """Verify terrestrial launch facilities."""
        pads = self.client.launchpads.list()
        self.assertGreaterEqual(len(pads), 4)
        names = [p.name for p in pads]
        self.assertIn("SLC-40", names)
        self.assertIn("LC-39A", names)
        self.assertIn("SLC-4E", names)
        self.assertIn("Starbase", names)

        starbase = self.client.launchpads.get("5e9e4502f3591855c03b262f")
        self.assertEqual(starbase.name, "Starbase")
        self.assertEqual(starbase.locality, "Boca Chica")
        self.assertEqual(starbase.region, "Texas")


if __name__ == "__main__":
    unittest.main()
