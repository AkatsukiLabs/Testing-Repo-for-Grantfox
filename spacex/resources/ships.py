"""Ships resource operations."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from spacex.types import QueryResult, Ship

if TYPE_CHECKING:
    from spacex.client import SpaceX


class ShipsResource:
    """Operations on SpaceX recovery vessels, ASDS droneships, and tugs."""

    def __init__(self, client: "SpaceX") -> None:
        self._client = client

    def list(self) -> List[Ship]:
        """Retrieve all recovery ships."""
        if self._client.offline:
            raw = self._client.engine.find_all("ships")
            return [Ship.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/ships")
        return [Ship.from_dict(item) for item in raw]

    def get(self, ship_id: str) -> Ship:
        """Retrieve single ship by ID."""
        if self._client.offline:
            raw = self._client.engine.find_one("ships", ship_id)
            return Ship.from_dict(raw)
        raw = self._client.request("GET", f"/ships/{ship_id}")
        return Ship.from_dict(raw)

    def query(
        self,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> QueryResult[Ship]:
        """Execute filtered, sorted, paginated query across ships."""
        if self._client.offline:
            return self._client.engine.execute_query(
                "ships",
                query=query,
                options=options,
                target_cls=Ship,
            )
        payload = {"query": query or {}, "options": options or {}}
        raw = self._client.request("POST", "/ships/query", json_data=payload)
        return QueryResult(
            docs=[Ship.from_dict(d) for d in raw.get("docs", [])],
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
