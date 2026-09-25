"""SpaceX API client and spaceflight engineering toolkit."""

from spacex.client import SpaceX, SpaceXClient
from spacex.exceptions import (
    APIConnectionError,
    NotFoundError,
    RateLimitError,
    SpaceXError,
    ValidationError,
)
from spacex.orbital import (
    calculate_apoapsis_periapsis,
    calculate_escape_velocity,
    calculate_orbital_period,
    calculate_orbital_velocity,
    calculate_payload_fraction,
    calculate_tsiolkovsky_delta_v,
)
from spacex.types import (
    Capsule,
    CompanyInfo,
    CrewMember,
    Launch,
    Launchpad,
    Payload,
    QueryResult,
    Rocket,
    Ship,
    Starlink,
)

__version__ = "1.0.0"

__all__ = [
    "SpaceX",
    "SpaceXClient",
    "SpaceXError",
    "NotFoundError",
    "ValidationError",
    "APIConnectionError",
    "RateLimitError",
    "Rocket",
    "Launch",
    "Capsule",
    "CrewMember",
    "Launchpad",
    "Ship",
    "Payload",
    "Starlink",
    "CompanyInfo",
    "QueryResult",
    "calculate_orbital_velocity",
    "calculate_orbital_period",
    "calculate_tsiolkovsky_delta_v",
    "calculate_escape_velocity",
    "calculate_apoapsis_periapsis",
    "calculate_payload_fraction",
]
