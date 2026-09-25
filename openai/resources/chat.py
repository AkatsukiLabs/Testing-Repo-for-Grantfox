"""Chat completions resource endpoint."""

from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Union

from openai.types import ChatCompletion, ChatCompletionChunk, ChatMessage

if TYPE_CHECKING:
    from openai.client import OpenAI


class ChatCompletions:
    """Completions endpoint under the chat namespace."""

    def __init__(self, client: "OpenAI") -> None:
        """Initialize chat completions resource with parent client reference."""
        self._client = client

    def create(
        self,
        model: str,
        messages: List[Union[Dict[str, Any], ChatMessage]],
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Create a model response for the given chat conversation.

        Args:
            model: Model identifier string.
            messages: List of message dictionaries or ChatMessage instances.
            temperature: Sampling temperature between 0.0 and 2.0.
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream back partial progress.
            stop: Up to 4 sequences where the API will stop generating further tokens.
            tools: A list of tools the model may call.
            tool_choice: Controls which tool is called by the model.

        Returns:
            ChatCompletion instance or an iterator yielding ChatCompletionChunk instances.
        """
        normalized_messages: List[Dict[str, Any]] = [
            m.to_dict() if isinstance(m, ChatMessage) else dict(m) for m in messages
        ]

        if self._client.is_local:
            return self._client.engine.create_chat_completion(
                model=model,
                messages=normalized_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                stop=stop,
                tools=tools,
                tool_choice=tool_choice,
            )

        payload: Dict[str, Any] = {
            "model": model,
            "messages": normalized_messages,
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stop is not None:
            payload["stop"] = stop
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice

        if stream:
            return self._client.request_stream("POST", "/chat/completions", payload)

        response_dict = self._client.request("POST", "/chat/completions", payload)
        return ChatCompletion.from_dict(response_dict)


class Chat:
    """Top-level chat resource exposing completions."""

    def __init__(self, client: "OpenAI") -> None:
        """Initialize chat resource with sub-endpoints."""
        self.completions = ChatCompletions(client)
