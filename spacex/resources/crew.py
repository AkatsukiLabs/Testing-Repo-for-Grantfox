"""Crew resource operations."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from spacex.types import CrewMember, QueryResult

if TYPE_CHECKING:
    from spacex.client import SpaceX


class CrewResource:
    """Operations on SpaceX astronaut and crew flight assignments."""

    def __init__(self, client: "SpaceX") -> None:
        self._client = client

    def list(self) -> List[CrewMember]:
        """Retrieve all crew members."""
        if self._client.offline:
            raw = self._client.engine.find_all("crew")
            return [CrewMember.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/crew")
        return [CrewMember.from_dict(item) for item in raw]

    def get(self, crew_id: str) -> CrewMember:
        """Retrieve single crew member by ID."""
        if self._client.offline:
            raw = self._client.engine.find_one("crew", crew_id)
            return CrewMember.from_dict(raw)
        raw = self._client.request("GET", f"/crew/{crew_id}")
        return CrewMember.from_dict(raw)

    def query(
        self,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> QueryResult[CrewMember]:
        """Execute filtered, sorted, paginated query across crew."""
        if self._client.offline:
            return self._client.engine.execute_query(
                "crew",
                query=query,
                options=options,
                target_cls=CrewMember,
            )
        payload = {"query": query or {}, "options": options or {}}
        raw = self._client.request("POST", "/crew/query", json_data=payload)
        return QueryResult(
            docs=[CrewMember.from_dict(d) for d in raw.get("docs", [])],
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
