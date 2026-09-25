"""Data models and response types for the OpenAI package."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Usage:
    """Token consumption metrics for API operations."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def to_dict(self) -> Dict[str, int]:
        """Convert usage object to dictionary representation."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Usage":
        """Construct Usage instance from dictionary."""
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )


@dataclass
class FunctionCall:
    """Function invocation details for tool execution."""
    name: str
    arguments: str

    def to_dict(self) -> Dict[str, str]:
        """Convert function call to dictionary representation."""
        return {
            "name": self.name,
            "arguments": self.arguments,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionCall":
        """Construct FunctionCall instance from dictionary."""
        return cls(
            name=data.get("name", ""),
            arguments=data.get("arguments", ""),
        )


@dataclass
class ToolCall:
    """Discrete tool invocation container."""
    id: str
    type: str = "function"
    function: FunctionCall = field(default_factory=lambda: FunctionCall(name="", arguments=""))

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool call to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type,
            "function": self.function.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCall":
        """Construct ToolCall instance from dictionary."""
        fn_data = data.get("function", {})
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "function"),
            function=FunctionCall.from_dict(fn_data),
        )


@dataclass
class ChatMessage:
    """Represents a discrete turn in a conversation."""
    role: str
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert chat message to dictionary representation."""
        payload: Dict[str, Any] = {"role": self.role}
        if self.content is not None:
            payload["content"] = self.content
        if self.name is not None:
            payload["name"] = self.name
        if self.tool_calls is not None:
            payload["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Construct ChatMessage instance from dictionary."""
        raw_tools = data.get("tool_calls")
        tools = [ToolCall.from_dict(tc) for tc in raw_tools] if raw_tools else None
        return cls(
            role=data.get("role", "user"),
            content=data.get("content"),
            name=data.get("name"),
            tool_calls=tools,
        )


@dataclass
class ChatCompletionChoice:
    """Individual completion choice returned by chat endpoints."""
    index: int
    message: ChatMessage
    finish_reason: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert choice to dictionary representation."""
        return {
            "index": self.index,
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionChoice":
        """Construct ChatCompletionChoice instance from dictionary."""
        return cls(
            index=data.get("index", 0),
            message=ChatMessage.from_dict(data.get("message", {})),
            finish_reason=data.get("finish_reason", "stop"),
        )


@dataclass
class ChatCompletionChunkDelta:
    """Incremental content delta in streaming responses."""
    role: Optional[str] = None
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert delta to dictionary representation."""
        payload: Dict[str, Any] = {}
        if self.role is not None:
            payload["role"] = self.role
        if self.content is not None:
            payload["content"] = self.content
        if self.tool_calls is not None:
            payload["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionChunkDelta":
        """Construct delta instance from dictionary."""
        raw_tools = data.get("tool_calls")
        tools = [ToolCall.from_dict(tc) for tc in raw_tools] if raw_tools else None
        return cls(
            role=data.get("role"),
            content=data.get("content"),
            tool_calls=tools,
        )


@dataclass
class ChatCompletionChunkChoice:
    """Discrete choice chunk in a streaming completion."""
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert choice chunk to dictionary representation."""
        return {
            "index": self.index,
            "delta": self.delta.to_dict(),
            "finish_reason": self.finish_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionChunkChoice":
        """Construct choice chunk from dictionary."""
        return cls(
            index=data.get("index", 0),
            delta=ChatCompletionChunkDelta.from_dict(data.get("delta", {})),
            finish_reason=data.get("finish_reason"),
        )


@dataclass
class ChatCompletion:
    """Full response object returned by chat completion requests."""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage

    def to_dict(self) -> Dict[str, Any]:
        """Convert completion to dictionary representation."""
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [c.to_dict() for c in self.choices],
            "usage": self.usage.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletion":
        """Construct ChatCompletion instance from dictionary."""
        choices = [ChatCompletionChoice.from_dict(c) for c in data.get("choices", [])]
        usage = Usage.from_dict(data.get("usage", {}))
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion"),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=choices,
            usage=usage,
        )


@dataclass
class ChatCompletionChunk:
    """Streamed event emitted during token generation."""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary representation."""
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [c.to_dict() for c in self.choices],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionChunk":
        """Construct chunk instance from dictionary."""
        choices = [ChatCompletionChunkChoice.from_dict(c) for c in data.get("choices", [])]
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion.chunk"),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=choices,
        )


@dataclass
class CompletionChoice:
    """Discrete choice returned by classic text completions."""
    text: str
    index: int
    finish_reason: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert completion choice to dictionary representation."""
        return {
            "text": self.text,
            "index": self.index,
            "finish_reason": self.finish_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompletionChoice":
        """Construct completion choice from dictionary."""
        return cls(
            text=data.get("text", ""),
            index=data.get("index", 0),
            finish_reason=data.get("finish_reason", "stop"),
        )


@dataclass
class Completion:
    """Full response object returned by text completion endpoints."""
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Usage

    def to_dict(self) -> Dict[str, Any]:
        """Convert completion to dictionary representation."""
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [c.to_dict() for c in self.choices],
            "usage": self.usage.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Completion":
        """Construct Completion instance from dictionary."""
        choices = [CompletionChoice.from_dict(c) for c in data.get("choices", [])]
        usage = Usage.from_dict(data.get("usage", {}))
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "text_completion"),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=choices,
            usage=usage,
        )


@dataclass
class Embedding:
    """Individual embedding vector container."""
    object: str
    embedding: List[float]
    index: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert embedding to dictionary representation."""
        return {
            "object": self.object,
            "embedding": self.embedding,
            "index": self.index,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Embedding":
        """Construct Embedding instance from dictionary."""
        return cls(
            object=data.get("object", "embedding"),
            embedding=data.get("embedding", []),
            index=data.get("index", 0),
        )


@dataclass
class EmbeddingResponse:
    """Full response object returned by embedding endpoints."""
    object: str
    data: List[Embedding]
    model: str
    usage: Usage

    def to_dict(self) -> Dict[str, Any]:
        """Convert embedding response to dictionary representation."""
        return {
            "object": self.object,
            "data": [e.to_dict() for e in self.data],
            "model": self.model,
            "usage": self.usage.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmbeddingResponse":
        """Construct EmbeddingResponse from dictionary."""
        items = [Embedding.from_dict(e) for e in data.get("data", [])]
        usage = Usage.from_dict(data.get("usage", {}))
        return cls(
            object=data.get("object", "list"),
            data=items,
            model=data.get("model", ""),
            usage=usage,
        )


@dataclass
class Model:
    """Model catalog descriptor."""
    id: str
    object: str
    created: int
    owned_by: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert model descriptor to dictionary representation."""
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "owned_by": self.owned_by,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Model":
        """Construct Model instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "model"),
            created=data.get("created", 0),
            owned_by=data.get("owned_by", ""),
        )
