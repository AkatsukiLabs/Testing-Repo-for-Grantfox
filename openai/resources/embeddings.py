"""Embeddings resource endpoint."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from openai.types import EmbeddingResponse

if TYPE_CHECKING:
    from openai.client import OpenAI


class Embeddings:
    """Embeddings generation endpoint."""

    def __init__(self, client: "OpenAI") -> None:
        """Initialize embeddings resource with parent client reference."""
        self._client = client

    def create(
        self,
        input: Union[str, List[str]],
        model: str = "text-embedding-3-small",
        dimensions: Optional[int] = None,
    ) -> EmbeddingResponse:
        """Create embedding vector representation of input text.

        Args:
            input: String or list of strings to embed.
            model: Embedding model identifier.
            dimensions: Number of dimensions the resulting output embeddings should have.

        Returns:
            EmbeddingResponse containing generated embedding vectors.
        """
        if self._client.is_local:
            return self._client.engine.create_embeddings(
                input_data=input,
                model=model,
                dimensions=dimensions,
            )

        payload: Dict[str, Any] = {
            "model": model,
            "input": input,
        }
        if dimensions is not None:
            payload["dimensions"] = dimensions

        response_dict = self._client.request("POST", "/embeddings", payload)
        return EmbeddingResponse.from_dict(response_dict)
