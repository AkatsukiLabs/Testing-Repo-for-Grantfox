"""Payloads resource operations."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from spacex.types import Payload, QueryResult

if TYPE_CHECKING:
    from spacex.client import SpaceX


class PayloadsResource:
    """Operations on SpaceX payloads, satellites, and spacecraft."""

    def __init__(self, client: "SpaceX") -> None:
        self._client = client

    def list(self) -> List[Payload]:
        """Retrieve all payloads."""
        if self._client.offline:
            raw = self._client.engine.find_all("payloads")
            return [Payload.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/payloads")
        return [Payload.from_dict(item) for item in raw]

    def get(self, payload_id: str) -> Payload:
        """Retrieve single payload by ID."""
        if self._client.offline:
            raw = self._client.engine.find_one("payloads", payload_id)
            return Payload.from_dict(raw)
        raw = self._client.request("GET", f"/payloads/{payload_id}")
        return Payload.from_dict(raw)

    def query(
        self,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> QueryResult[Payload]:
        """Execute filtered, sorted, paginated query across payloads."""
        if self._client.offline:
            return self._client.engine.execute_query(
                "payloads",
                query=query,
                options=options,
                target_cls=Payload,
            )
        payload = {"query": query or {}, "options": options or {}}
        raw = self._client.request("POST", "/payloads/query", json_data=payload)
        return QueryResult(
            docs=[Payload.from_dict(d) for d in raw.get("docs", [])],
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
