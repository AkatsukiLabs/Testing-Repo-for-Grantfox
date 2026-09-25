"""Starlink constellation resource operations."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from spacex.types import QueryResult, Starlink

if TYPE_CHECKING:
    from spacex.client import SpaceX


class StarlinkResource:
    """Operations on Starlink broadband satellite constellation nodes."""

    def __init__(self, client: "SpaceX") -> None:
        self._client = client

    def list(self) -> List[Starlink]:
        """Retrieve all Starlink satellite records."""
        if self._client.offline:
            raw = self._client.engine.find_all("starlink")
            return [Starlink.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/starlink")
        return [Starlink.from_dict(item) for item in raw]

    def get(self, starlink_id: str) -> Starlink:
        """Retrieve single Starlink satellite by ID."""
        if self._client.offline:
            raw = self._client.engine.find_one("starlink", starlink_id)
            return Starlink.from_dict(raw)
        raw = self._client.request("GET", f"/starlink/{starlink_id}")
        return Starlink.from_dict(raw)

    def query(
        self,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> QueryResult[Starlink]:
        """Execute filtered, sorted, paginated query across Starlink constellation."""
        if self._client.offline:
            return self._client.engine.execute_query(
                "starlink",
                query=query,
                options=options,
                target_cls=Starlink,
            )
        payload = {"query": query or {}, "options": options or {}}
        raw = self._client.request("POST", "/starlink/query", json_data=payload)
        return QueryResult(
            docs=[Starlink.from_dict(d) for d in raw.get("docs", [])],
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
