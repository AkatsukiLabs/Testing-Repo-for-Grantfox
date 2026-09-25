"""Capsules resource operations."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from spacex.types import Capsule, QueryResult

if TYPE_CHECKING:
    from spacex.client import SpaceX


class CapsulesResource:
    """Operations on SpaceX Dragon capsule pressure vessels."""

    def __init__(self, client: "SpaceX") -> None:
        self._client = client

    def list(self) -> List[Capsule]:
        """Retrieve all capsules."""
        if self._client.offline:
            raw = self._client.engine.find_all("capsules")
            return [Capsule.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/capsules")
        return [Capsule.from_dict(item) for item in raw]

    def get(self, capsule_id: str) -> Capsule:
        """Retrieve single capsule by ID."""
        if self._client.offline:
            raw = self._client.engine.find_one("capsules", capsule_id)
            return Capsule.from_dict(raw)
        raw = self._client.request("GET", f"/capsules/{capsule_id}")
        return Capsule.from_dict(raw)

    def query(
        self,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> QueryResult[Capsule]:
        """Execute filtered, sorted, paginated query across capsules."""
        if self._client.offline:
            return self._client.engine.execute_query(
                "capsules",
                query=query,
                options=options,
                target_cls=Capsule,
            )
        payload = {"query": query or {}, "options": options or {}}
        raw = self._client.request("POST", "/capsules/query", json_data=payload)
        return QueryResult(
            docs=[Capsule.from_dict(d) for d in raw.get("docs", [])],
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
