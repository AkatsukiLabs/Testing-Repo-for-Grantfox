"""Orbital mechanics and rocket equation calculation utilities."""

import math
from typing import Dict, Tuple

GRAVITATIONAL_CONSTANTS: Dict[str, Dict[str, float]] = {
    "earth": {
        "mu": 3.986004418e14,
        "radius_km": 6371.0,
    },
    "mars": {
        "mu": 4.282837e13,
        "radius_km": 3389.5,
    },
    "moon": {
        "mu": 4.9048695e12,
        "radius_km": 1737.4,
    },
}

STANDARD_GRAVITY = 9.80665


def calculate_orbital_velocity(altitude_km: float, body: str = "earth") -> float:
    """Calculate circular orbital velocity in meters per second at given altitude.

    Args:
        altitude_km: Altitude above surface in kilometers.
        body: Celestial body name ('earth', 'mars', 'moon').

    Returns:
        Orbital velocity in m/s.
    """
    key = body.lower()
    if key not in GRAVITATIONAL_CONSTANTS:
        raise ValueError(f"Unsupported celestial body: {body}")
    consts = GRAVITATIONAL_CONSTANTS[key]
    radius_m = (consts["radius_km"] + altitude_km) * 1000.0
    if radius_m <= 0:
        raise ValueError("Orbital radius must be positive")
    return math.sqrt(consts["mu"] / radius_m)


def calculate_orbital_period(semi_major_axis_km: float, body: str = "earth") -> float:
    """Calculate orbital period in seconds for a given semi-major axis.

    Args:
        semi_major_axis_km: Semi-major axis in kilometers.
        body: Celestial body name.

    Returns:
        Period in seconds.
    """
    key = body.lower()
    if key not in GRAVITATIONAL_CONSTANTS:
        raise ValueError(f"Unsupported celestial body: {body}")
    consts = GRAVITATIONAL_CONSTANTS[key]
    a_m = semi_major_axis_km * 1000.0
    if a_m <= 0:
        raise ValueError("Semi-major axis must be positive")
    return 2.0 * math.pi * math.sqrt((a_m**3) / consts["mu"])


def calculate_tsiolkovsky_delta_v(
    dry_mass_kg: float,
    propellant_mass_kg: float,
    isp_sec: float,
    g0: float = STANDARD_GRAVITY,
) -> float:
    """Calculate ideal velocity change (delta-v) via Tsiolkovsky rocket equation.

    Args:
        dry_mass_kg: Vehicle dry mass in kg.
        propellant_mass_kg: Usable propellant mass in kg.
        isp_sec: Specific impulse in seconds.
        g0: Gravitational acceleration in m/s^2.

    Returns:
        Delta-v in meters per second.
    """
    if dry_mass_kg <= 0:
        raise ValueError("Dry mass must be strictly positive")
    if propellant_mass_kg < 0:
        raise ValueError("Propellant mass cannot be negative")
    if isp_sec <= 0:
        raise ValueError("Specific impulse must be strictly positive")
    initial_mass = dry_mass_kg + propellant_mass_kg
    return isp_sec * g0 * math.log(initial_mass / dry_mass_kg)


def calculate_escape_velocity(altitude_km: float, body: str = "earth") -> float:
    """Calculate parabolic escape velocity in meters per second at given altitude.

    Args:
        altitude_km: Altitude above surface in kilometers.
        body: Celestial body name.

    Returns:
        Escape velocity in m/s.
    """
    circular_v = calculate_orbital_velocity(altitude_km, body=body)
    return math.sqrt(2.0) * circular_v


def calculate_apoapsis_periapsis(
    semi_major_axis_km: float,
    eccentricity: float,
    body: str = "earth",
) -> Tuple[float, float]:
    """Calculate apoapsis and periapsis altitudes in kilometers.

    Args:
        semi_major_axis_km: Semi-major axis in kilometers.
        eccentricity: Orbital eccentricity (0 <= e < 1 for elliptical).
        body: Celestial body name.

    Returns:
        Tuple of (apoapsis_altitude_km, periapsis_altitude_km).
    """
    if eccentricity < 0 or eccentricity >= 1.0:
        raise ValueError("Eccentricity must be in range [0, 1) for bound orbit")
    key = body.lower()
    if key not in GRAVITATIONAL_CONSTANTS:
        raise ValueError(f"Unsupported celestial body: {body}")
    radius_km = GRAVITATIONAL_CONSTANTS[key]["radius_km"]
    apoapsis_km = semi_major_axis_km * (1.0 + eccentricity) - radius_km
    periapsis_km = semi_major_axis_km * (1.0 - eccentricity) - radius_km
    return apoapsis_km, periapsis_km


def calculate_payload_fraction(
    dry_mass_kg: float,
    propellant_mass_kg: float,
    payload_mass_kg: float,
) -> float:
    """Calculate ratio of payload mass to total liftoff mass.

    Args:
        dry_mass_kg: Vehicle dry structure mass.
        propellant_mass_kg: Propellant load mass.
        payload_mass_kg: Payload mass.

    Returns:
        Dimensionless payload fraction.
    """
    total_mass = dry_mass_kg + propellant_mass_kg + payload_mass_kg
    if total_mass <= 0:
        raise ValueError("Total mass must be strictly positive")
    return payload_mass_kg / total_mass


def calculate_hohmann_transfer(
    initial_altitude_km: float,
    target_altitude_km: float,
    body: str = "earth",
) -> Tuple[float, float, float]:
    """Compute Hohmann transfer delta-v between two coplanar circular orbits.

    Args:
        initial_altitude_km: Initial circular orbit altitude in km.
        target_altitude_km: Target circular orbit altitude in km.
        body: Celestial body name.

    Returns:
        Tuple of (dv1_m_s, dv2_m_s, total_dv_m_s).
    """
    key = body.lower()
    if key not in GRAVITATIONAL_CONSTANTS:
        raise ValueError(f"Unsupported celestial body: {body}")
    consts = GRAVITATIONAL_CONSTANTS[key]
    mu = consts["mu"]
    r_km = consts["radius_km"]
    r1 = (r_km + initial_altitude_km) * 1000.0
    r2 = (r_km + target_altitude_km) * 1000.0
    if r1 <= 0 or r2 <= 0:
        raise ValueError("Orbital radii must be positive")
    v1 = math.sqrt(mu / r1)
    v2 = math.sqrt(mu / r2)
    a_tx = (r1 + r2) / 2.0
    v_tx1 = math.sqrt(mu * (2.0 / r1 - 1.0 / a_tx))
    v_tx2 = math.sqrt(mu * (2.0 / r2 - 1.0 / a_tx))
    dv1 = abs(v_tx1 - v1)
    dv2 = abs(v2 - v_tx2)
    return dv1, dv2, dv1 + dv2
