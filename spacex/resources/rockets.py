"""Rockets resource operations."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from spacex.types import QueryResult, Rocket

if TYPE_CHECKING:
    from spacex.client import SpaceX


class RocketsResource:
    """Operations on SpaceX rocket vehicle designs and capabilities."""

    def __init__(self, client: "SpaceX") -> None:
        self._client = client

    def list(self) -> List[Rocket]:
        """Retrieve all SpaceX rocket vehicles."""
        if self._client.offline:
            raw = self._client.engine.find_all("rockets")
            return [Rocket.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/rockets")
        return [Rocket.from_dict(item) for item in raw]

    def get(self, rocket_id: str) -> Rocket:
        """Retrieve single rocket specification by ID."""
        if self._client.offline:
            raw = self._client.engine.find_one("rockets", rocket_id)
            return Rocket.from_dict(raw)
        raw = self._client.request("GET", f"/rockets/{rocket_id}")
        return Rocket.from_dict(raw)

    def query(
        self,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> QueryResult[Rocket]:
        """Perform filtered, sorted, paginated query on rockets collection."""
        if self._client.offline:
            return self._client.engine.execute_query(
                "rockets",
                query=query,
                options=options,
                target_cls=Rocket,
            )
        payload = {"query": query or {}, "options": options or {}}
        raw = self._client.request("POST", "/rockets/query", json_data=payload)
        return QueryResult(
            docs=[Rocket.from_dict(d) for d in raw.get("docs", [])],
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
