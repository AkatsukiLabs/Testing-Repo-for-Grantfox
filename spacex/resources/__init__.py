"""Resource exports for SpaceX client."""

from spacex.resources.capsules import CapsulesResource
from spacex.resources.company import CompanyResource
from spacex.resources.crew import CrewResource
from spacex.resources.launches import LaunchesResource
from spacex.resources.launchpads import LaunchpadsResource
from spacex.resources.payloads import PayloadsResource
from spacex.resources.rockets import RocketsResource
from spacex.resources.ships import ShipsResource
from spacex.resources.starlink import StarlinkResource

__all__ = [
    "RocketsResource",
    "LaunchesResource",
    "CapsulesResource",
    "CrewResource",
    "LaunchpadsResource",
    "ShipsResource",
    "PayloadsResource",
    "StarlinkResource",
    "CompanyResource",
]
