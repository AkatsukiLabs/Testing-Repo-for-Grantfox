"""Main SpaceX API client and local offline interface."""

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple

from spacex.engine import SpaceXEngine
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
    calculate_hohmann_transfer,
    calculate_orbital_period,
    calculate_orbital_velocity,
    calculate_payload_fraction,
    calculate_tsiolkovsky_delta_v,
)
from spacex.resources import (
    CapsulesResource,
    CompanyResource,
    CrewResource,
    LaunchesResource,
    LaunchpadsResource,
    PayloadsResource,
    RocketsResource,
    ShipsResource,
    StarlinkResource,
)


class SpaceX:
    """Unified client for SpaceX spaceflight data and telemetry."""

    def __init__(
        self,
        base_url: str = "https://api.spacexdata.com/v4",
        offline: bool = True,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.offline = offline
        self.timeout = timeout
        self.engine = SpaceXEngine()

        self.rockets = RocketsResource(self)
        self.launches = LaunchesResource(self)
        self.capsules = CapsulesResource(self)
        self.crew = CrewResource(self)
        self.launchpads = LaunchpadsResource(self)
        self.ships = ShipsResource(self)
        self.payloads = PayloadsResource(self)
        self.starlink = StarlinkResource(self)
        self.company = CompanyResource(self)

    def __enter__(self) -> "SpaceX":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Execute HTTP request against remote SpaceX API endpoint."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        data_bytes = None
        headers = {"User-Agent": "SpaceX-Python-SDK/1.0"}
        if json_data is not None:
            data_bytes = json.dumps(json_data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(
            url=url,
            data=data_bytes,
            headers=headers,
            method=method.upper(),
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw_body = resp.read().decode("utf-8")
                if not raw_body:
                    return None
                return json.loads(raw_body)
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8", errors="replace")
            try:
                parsed_err = json.loads(err_body)
            except Exception:
                parsed_err = err_body

            if err.code == 404:
                raise NotFoundError(
                    f"Resource not found at {path}",
                    status_code=err.code,
                ) from err
            if err.code == 400:
                raise ValidationError(
                    f"Invalid request to {path}: {err_body}",
                    status_code=err.code,
                ) from err
            if err.code == 429:
                retry_after = None
                raw_retry = err.headers.get("Retry-After")
                if raw_retry and raw_retry.isdigit():
                    retry_after = int(raw_retry)
                raise RateLimitError(
                    "Rate limit exceeded on SpaceX API",
                    status_code=err.code,
                    retry_after=retry_after,
                ) from err

            raise SpaceXError(
                f"HTTP {err.code}: {err.reason}",
                status_code=err.code,
                response_body=parsed_err,
            ) from err
        except urllib.error.URLError as err:
            raise APIConnectionError(
                f"Failed to connect to {url}: {err.reason}"
            ) from err
        except TimeoutError as err:
            raise APIConnectionError(
                f"Request to {url} timed out after {self.timeout}s"
            ) from err

    def calculate_orbital_velocity(
        self,
        altitude_km: float,
        body: str = "earth",
    ) -> float:
        """Calculate circular orbital velocity in meters per second."""
        return calculate_orbital_velocity(altitude_km, body=body)

    def calculate_orbital_period(
        self,
        semi_major_axis_km: float,
        body: str = "earth",
    ) -> float:
        """Calculate orbital period in seconds."""
        return calculate_orbital_period(semi_major_axis_km, body=body)

    def calculate_tsiolkovsky_delta_v(
        self,
        dry_mass_kg: float,
        propellant_mass_kg: float,
        isp_sec: float,
    ) -> float:
        """Calculate ideal delta-v in meters per second."""
        return calculate_tsiolkovsky_delta_v(
            dry_mass_kg, propellant_mass_kg, isp_sec
        )

    def calculate_escape_velocity(
        self,
        altitude_km: float,
        body: str = "earth",
    ) -> float:
        """Calculate parabolic escape velocity in meters per second."""
        return calculate_escape_velocity(altitude_km, body=body)

    def calculate_apoapsis_periapsis(
        self,
        semi_major_axis_km: float,
        eccentricity: float,
        body: str = "earth",
    ) -> Tuple[float, float]:
        """Calculate apoapsis and periapsis altitudes in kilometers."""
        return calculate_apoapsis_periapsis(
            semi_major_axis_km, eccentricity, body=body
        )

    def calculate_payload_fraction(
        self,
        dry_mass_kg: float,
        propellant_mass_kg: float,
        payload_mass_kg: float,
    ) -> float:
        """Calculate dimensionless payload fraction."""
        return calculate_payload_fraction(
            dry_mass_kg, propellant_mass_kg, payload_mass_kg
        )

    def calculate_hohmann_transfer(
        self,
        initial_altitude_km: float,
        target_altitude_km: float,
        body: str = "earth",
    ) -> Tuple[float, float, float]:
        """Compute Hohmann transfer delta-v between two circular orbits."""
        return calculate_hohmann_transfer(
            initial_altitude_km, target_altitude_km, body=body
        )


SpaceXClient = SpaceX
