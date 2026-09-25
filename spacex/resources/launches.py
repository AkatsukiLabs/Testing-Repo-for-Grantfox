"""Launches resource operations."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from spacex.exceptions import NotFoundError
from spacex.types import Launch, QueryResult

if TYPE_CHECKING:
    from spacex.client import SpaceX


class LaunchesResource:
    """Operations on SpaceX launch events and missions."""

    def __init__(self, client: "SpaceX") -> None:
        self._client = client

    def list(self) -> List[Launch]:
        """Retrieve all launches."""
        if self._client.offline:
            raw = self._client.engine.find_all("launches")
            return [Launch.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/launches")
        return [Launch.from_dict(item) for item in raw]

    def get(self, launch_id: str) -> Launch:
        """Retrieve single launch record by ID."""
        if self._client.offline:
            raw = self._client.engine.find_one("launches", launch_id)
            return Launch.from_dict(raw)
        raw = self._client.request("GET", f"/launches/{launch_id}")
        return Launch.from_dict(raw)

    def latest(self) -> Launch:
        """Retrieve the most recent completed launch."""
        if self._client.offline:
            past_launches = [
                l for l in self._client.engine.launches
                if not l.get("upcoming", False)
            ]
            if not past_launches:
                raise NotFoundError("No completed launches recorded")
            sorted_launches = sorted(
                past_launches,
                key=lambda x: x.get("date_unix", 0),
                reverse=True,
            )
            return Launch.from_dict(sorted_launches[0])
        raw = self._client.request("GET", "/launches/latest")
        return Launch.from_dict(raw)

    def next(self) -> Launch:
        """Retrieve the closest upcoming scheduled launch."""
        if self._client.offline:
            upcoming_launches = [
                l for l in self._client.engine.launches
                if l.get("upcoming", False)
            ]
            if not upcoming_launches:
                raise NotFoundError("No upcoming launches recorded")
            sorted_launches = sorted(
                upcoming_launches,
                key=lambda x: x.get("date_unix", 0),
            )
            return Launch.from_dict(sorted_launches[0])
        raw = self._client.request("GET", "/launches/next")
        return Launch.from_dict(raw)

    def upcoming(self) -> List[Launch]:
        """Retrieve all upcoming scheduled launches."""
        if self._client.offline:
            raw = [
                l for l in self._client.engine.launches
                if l.get("upcoming", False)
            ]
            return [Launch.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/launches/upcoming")
        return [Launch.from_dict(item) for item in raw]

    def past(self) -> List[Launch]:
        """Retrieve all completed historical launches."""
        if self._client.offline:
            raw = [
                l for l in self._client.engine.launches
                if not l.get("upcoming", False)
            ]
            return [Launch.from_dict(item) for item in raw]
        raw = self._client.request("GET", "/launches/past")
        return [Launch.from_dict(item) for item in raw]

    def query(
        self,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> QueryResult[Launch]:
        """Execute filtered, sorted, paginated query across launches."""
        if self._client.offline:
            return self._client.engine.execute_query(
                "launches",
                query=query,
                options=options,
                target_cls=Launch,
            )
        payload = {"query": query or {}, "options": options or {}}
        raw = self._client.request("POST", "/launches/query", json_data=payload)
        return QueryResult(
            docs=[Launch.from_dict(d) for d in raw.get("docs", [])],
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
