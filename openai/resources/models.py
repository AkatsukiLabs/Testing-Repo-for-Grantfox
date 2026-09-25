"""Models resource endpoint."""

from typing import TYPE_CHECKING, Any, Dict, List

from openai.types import Model

if TYPE_CHECKING:
    from openai.client import OpenAI


class Models:
    """Model catalog endpoint."""

    def __init__(self, client: "OpenAI") -> None:
        """Initialize models resource with parent client reference."""
        self._client = client

    def list(self) -> List[Model]:
        """List all available models.

        Returns:
            List of Model objects.
        """
        if self._client.is_local:
            return self._client.engine.list_models()

        response_dict = self._client.request("GET", "/models")
        return [Model.from_dict(m) for m in response_dict.get("data", [])]

    def retrieve(self, model: str) -> Model:
        """Retrieve details for a specific model.

        Args:
            model: Model identifier string.

        Returns:
            Model descriptor instance.
        """
        if self._client.is_local:
            return self._client.engine.get_model(model)

        response_dict = self._client.request("GET", f"/models/{model}")
        return Model.from_dict(response_dict)
