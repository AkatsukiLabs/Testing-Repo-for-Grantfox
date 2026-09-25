"""Launchpads resource operations."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from spacex.types import Launchpad, QueryResult

if TYPE_CHECKING:
    from spacex.client import SpaceX


class LaunchpadsResource:
    """Operations on SpaceX launch facility infrastructures."""

    def __init__(self, client: "SpaceX") -> None:
        self._client = client

    def list(self) -> List[Launchpad]:
        """Retrieve all launchpads."""
        if self._client.offline:
            raw = self._client.engine.find_all("launchpads")
            return [Launchpad.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/launchpads")
        return [Launchpad.from_dict(item) for item in raw]

    def get(self, launchpad_id: str) -> Launchpad:
        """Retrieve single launchpad by ID."""
        if self._client.offline:
            raw = self._client.engine.find_one("launchpads", launchpad_id)
            return Launchpad.from_dict(raw)
        raw = self._client.request("GET", f"/launchpads/{launchpad_id}")
        return Launchpad.from_dict(raw)

    def query(
        self,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> QueryResult[Launchpad]:
        """Execute filtered, sorted, paginated query across launchpads."""
        if self._client.offline:
            return self._client.engine.execute_query(
                "launchpads",
                query=query,
                options=options,
                target_cls=Launchpad,
            )
        payload = {"query": query or {}, "options": options or {}}
        raw = self._client.request("POST", "/launchpads/query", json_data=payload)
        return QueryResult(
            docs=[Launchpad.from_dict(d) for d in raw.get("docs", [])],
            total_docs=raw.get("totalDocs", 0),
            limit=raw.get("limit", 10),
            total_pages=raw.get("totalPages", 1),
            page=raw.get("page", 1),
            paging_counter=raw.get("pagingCounter", 1),
            has_prev_page=raw.get("hasPrevPage", False),
            has_next_page=raw.get("hasNextPage", False),
            prev_page=raw.get("prevPage"),
            next_page=raw.get("nextPage"),
        )
