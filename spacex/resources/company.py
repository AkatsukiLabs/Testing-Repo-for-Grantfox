"""Company resource operations."""

from typing import TYPE_CHECKING

from spacex.types import CompanyInfo

if TYPE_CHECKING:
    from spacex.client import SpaceX


class CompanyResource:
    """Operations on SpaceX corporate structure and details."""

    def __init__(self, client: "SpaceX") -> None:
        self._client = client

    def get(self) -> CompanyInfo:
        """Retrieve SpaceX company metadata and executive overview."""
        if self._client.offline:
            return CompanyInfo.from_dict(self._client.engine.company)
        raw = self._client.request("GET", "/company")
        return CompanyInfo.from_dict(raw)
