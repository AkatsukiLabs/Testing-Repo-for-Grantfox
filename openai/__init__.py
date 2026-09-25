"""OpenAI Python library for interacting with OpenAI API and local models."""

from openai.client import OpenAI
from openai.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    OpenAIError,
    RateLimitError,
)
from openai.types import (
    ChatCompletion,
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
    ChatMessage,
    Completion,
    CompletionChoice,
    Embedding,
    EmbeddingResponse,
    FunctionCall,
    Model,
    ToolCall,
    Usage,
)

__version__ = "1.0.0"

__all__ = [
    "OpenAI",
    "OpenAIError",
    "APIError",
    "AuthenticationError",
    "BadRequestError",
    "NotFoundError",
    "RateLimitError",
    "APIConnectionError",
    "ChatCompletion",
    "ChatCompletionChoice",
    "ChatCompletionChunk",
    "ChatCompletionChunkChoice",
    "ChatCompletionChunkDelta",
    "ChatMessage",
    "Completion",
    "CompletionChoice",
    "Embedding",
    "EmbeddingResponse",
    "FunctionCall",
    "Model",
    "ToolCall",
    "Usage",
]
