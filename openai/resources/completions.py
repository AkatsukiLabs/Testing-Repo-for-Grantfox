"""Legacy text completions resource endpoint."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from openai.types import Completion

if TYPE_CHECKING:
    from openai.client import OpenAI


class Completions:
    """Completions endpoint for text prompting."""

    def __init__(self, client: "OpenAI") -> None:
        """Initialize completions endpoint with parent client reference."""
        self._client = client

    def create(
        self,
        model: str,
        prompt: Union[str, List[str]],
        max_tokens: int = 16,
        temperature: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
    ) -> Completion:
        """Create a completion for the provided prompt.

        Args:
            model: Model identifier string.
            prompt: Text prompt or list of prompt strings.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            stop: Up to 4 stop sequences.

        Returns:
            Completion instance.
        """
        if self._client.is_local:
            return self._client.engine.create_completion(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop,
            )

        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if stop is not None:
            payload["stop"] = stop

        response_dict = self._client.request("POST", "/completions", payload)
        return Completion.from_dict(response_dict)
