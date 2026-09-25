"""Unit tests for orbital mechanics and propulsion calculations."""

import math
import unittest

from spacex import (
    SpaceX,
    calculate_apoapsis_periapsis,
    calculate_escape_velocity,
    calculate_orbital_period,
    calculate_orbital_velocity,
    calculate_payload_fraction,
    calculate_tsiolkovsky_delta_v,
)
from spacex.orbital import calculate_hohmann_transfer


class TestOrbitalMechanics(unittest.TestCase):
    """Test suite for orbital calculations, escape velocity, and rocket equations."""

    def setUp(self) -> None:
        """Initialize client for helper method testing."""
        self.client = SpaceX()

    def test_circular_orbital_velocity_iss_altitude(self) -> None:
        """Verify orbital velocity at 400 km ISS altitude (~7672 m/s)."""
        v_orbit = calculate_orbital_velocity(altitude_km=400.0, body="earth")
        self.assertAlmostEqual(v_orbit, 7672.6, delta=5.0)

    def test_orbital_period_iss_altitude(self) -> None:
        """Verify orbital period at 6771 km semi-major axis (~92.5 minutes)."""
        period_seconds = calculate_orbital_period(semi_major_axis_km=6771.0, body="earth")
        period_minutes = period_seconds / 60.0
        self.assertAlmostEqual(period_minutes, 92.56, delta=0.5)

    def test_tsiolkovsky_delta_v(self) -> None:
        """Verify ideal delta-v calculation using Tsiolkovsky equation."""
        dry_mass = 22200.0
        prop_mass = 395700.0
        isp = 311.0
        dv = calculate_tsiolkovsky_delta_v(
            dry_mass_kg=dry_mass,
            propellant_mass_kg=prop_mass,
            isp_sec=isp,
        )
        expected_ratio = (dry_mass + prop_mass) / dry_mass
        expected_dv = isp * 9.80665 * math.log(expected_ratio)
        self.assertAlmostEqual(dv, expected_dv, places=4)
        self.assertGreater(dv, 8900.0)

    def test_escape_velocity_relation(self) -> None:
        """Verify escape velocity is exactly sqrt(2) times orbital velocity."""
        v_circ = calculate_orbital_velocity(altitude_km=300.0, body="earth")
        v_esc = calculate_escape_velocity(altitude_km=300.0, body="earth")
        self.assertAlmostEqual(v_esc, math.sqrt(2.0) * v_circ, places=4)

    def test_apoapsis_periapsis_calculation(self) -> None:
        """Verify apsis altitudes for eccentric orbit."""
        semi_major_axis = 7000.0
        eccentricity = 0.05
        ra, rp = calculate_apoapsis_periapsis(
            semi_major_axis_km=semi_major_axis,
            eccentricity=eccentricity,
            body="earth",
        )
        self.assertAlmostEqual(ra, 7000.0 * 1.05 - 6371.0, places=4)
        self.assertAlmostEqual(rp, 7000.0 * 0.95 - 6371.0, places=4)
        self.assertGreater(ra, rp)

    def test_payload_fraction(self) -> None:
        """Verify structural payload fraction calculation."""
        dry = 30000.0
        prop = 400000.0
        payload = 15000.0
        fraction = calculate_payload_fraction(dry, prop, payload)
        expected = payload / (dry + prop + payload)
        self.assertAlmostEqual(fraction, expected, places=5)

    def test_hohmann_transfer_leo_to_geo(self) -> None:
        """Verify two-impulse transfer calculation from LEO to GEO altitude."""
        dv1, dv2, total = calculate_hohmann_transfer(
            initial_altitude_km=400.0,
            target_altitude_km=35786.0,
            body="earth",
        )
        self.assertGreater(dv1, 0.0)
        self.assertGreater(dv2, 0.0)
        self.assertEqual(total, dv1 + dv2)
        self.assertAlmostEqual(total, 3850.0, delta=100.0)

    def test_client_orbital_methods(self) -> None:
        """Verify client convenience methods mirror standalone calculations."""
        v1 = self.client.calculate_orbital_velocity(500.0)
        v2 = calculate_orbital_velocity(500.0)
        self.assertEqual(v1, v2)


if __name__ == "__main__":
    unittest.main()
