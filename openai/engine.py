"""Deterministic offline execution engine for local inference and simulation."""

import hashlib
import json
import math
import time
import uuid
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from openai.exceptions import BadRequestError, NotFoundError
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


class LocalEngine:
    """Local inference engine delivering deterministic completions and embeddings."""

    DEFAULT_MODELS: Dict[str, Dict[str, Any]] = {
        "gpt-4o": {"created": 1715367049, "owned_by": "system"},
        "gpt-4o-mini": {"created": 1721245000, "owned_by": "system"},
        "gpt-4-turbo": {"created": 1712361441, "owned_by": "system"},
        "gpt-3.5-turbo": {"created": 1677610602, "owned_by": "openai"},
        "text-embedding-3-small": {"created": 1705948997, "owned_by": "system"},
        "text-embedding-3-large": {"created": 1705948997, "owned_by": "system"},
        "text-embedding-ada-002": {"created": 1671217299, "owned_by": "openai-internal"},
    }

    def __init__(self) -> None:
        """Initialize the local engine instance."""
        self.models_catalog: Dict[str, Dict[str, Any]] = dict(self.DEFAULT_MODELS)

    def list_models(self) -> List[Model]:
        """Return all available models from the catalog."""
        return [
            Model(id=model_id, object="model", created=meta["created"], owned_by=meta["owned_by"])
            for model_id, meta in self.models_catalog.items()
        ]

    def get_model(self, model_id: str) -> Model:
        """Retrieve metadata for a specific model identifier."""
        if model_id not in self.models_catalog:
            raise NotFoundError(f"The model '{model_id}' does not exist.", status_code=404)
        meta = self.models_catalog[model_id]
        return Model(id=model_id, object="model", created=meta["created"], owned_by=meta["owned_by"])

    def count_tokens(self, text: str) -> int:
        """Calculate approximate token count from text using whitespace and punctuation boundaries."""
        if not text:
            return 0
        words = text.strip().split()
        punctuation_count = sum(text.count(p) for p in ',.!?:;-()[]{}')
        return max(1, len(words) + (punctuation_count // 3))

    def _generate_response_content(self, messages: List[Dict[str, Any]]) -> str:
        """Synthesize coherent deterministic reply from input message history."""
        user_messages: List[str] = []
        system_instruction: str = ""

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "") or ""
            if role == "system":
                system_instruction = content
            elif role == "user":
                user_messages.append(content)

        last_query = user_messages[-1] if user_messages else "Hello"
        last_query_lower = last_query.lower()

        if "calculate" in last_query_lower or "+" in last_query_lower or "*" in last_query_lower:
            response = f"Computed response for: {last_query.strip()}"
        elif "who are you" in last_query_lower:
            response = "I am an artificial intelligence model designed to process natural language queries."
        elif system_instruction:
            response = f"Acknowledged instruction: {system_instruction}. Query processed: {last_query}"
        else:
            response = f"Response to: {last_query.strip()}"

        return response

    def _detect_tool_calls(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> Optional[List[ToolCall]]:
        """Determine whether incoming query triggers configured tools."""
        if not tools:
            return None

        if tool_choice == "none":
            return None

        last_content = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_content = msg.get("content", "") or ""
                break

        last_content_lower = last_content.lower()

        for tool in tools:
            fn = tool.get("function", {})
            fn_name = fn.get("name", "")
            fn_desc = fn.get("description", "").lower()

            triggered = False
            if isinstance(tool_choice, dict) and tool_choice.get("function", {}).get("name") == fn_name:
                triggered = True
            elif tool_choice == "required":
                triggered = True
            elif fn_name.lower() in last_content_lower or any(word in last_content_lower for word in fn_desc.split() if len(word) > 4):
                triggered = True

            if triggered:
                call_id = f"call_{hashlib.md5(f'{fn_name}{last_content}'.encode()).hexdigest()[:12]}"
                parameters = fn.get("parameters", {}).get("properties", {})
                args: Dict[str, Any] = {}
                for param_name in parameters:
                    args[param_name] = f"extracted_{param_name}"
                return [
                    ToolCall(
                        id=call_id,
                        type="function",
                        function=FunctionCall(name=fn_name, arguments=json.dumps(args)),
                    )
                ]

        return None

    def create_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Execute a chat completion request either as full response or streaming generator."""
        if not messages:
            raise BadRequestError("The 'messages' array cannot be empty.", status_code=400)

        tool_calls = self._detect_tool_calls(messages, tools, tool_choice)

        if tool_calls:
            finish_reason = "tool_calls"
            full_content = None
        else:
            finish_reason = "stop"
            full_content = self._generate_response_content(messages)

            stop_list: List[str] = [stop] if isinstance(stop, str) else (stop or [])
            for stop_token in stop_list:
                if stop_token in full_content:
                    full_content = full_content.split(stop_token)[0]
                    finish_reason = "stop"
                    break

            if max_tokens is not None and max_tokens > 0:
                words = full_content.split()
                if len(words) > max_tokens:
                    full_content = " ".join(words[:max_tokens])
                    finish_reason = "length"

        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created_timestamp = int(time.time())

        if stream:
            return self._stream_chat_completion(
                completion_id=completion_id,
                created_timestamp=created_timestamp,
                model=model,
                content=full_content,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
            )

        prompt_tokens = sum(self.count_tokens(m.get("content", "") or "") for m in messages)
        completion_tokens = self.count_tokens(full_content) if full_content else 15
        total_tokens = prompt_tokens + completion_tokens

        choice = ChatCompletionChoice(
            index=0,
            message=ChatMessage(
                role="assistant",
                content=full_content,
                tool_calls=tool_calls,
            ),
            finish_reason=finish_reason,
        )

        return ChatCompletion(
            id=completion_id,
            object="chat.completion",
            created=created_timestamp,
            model=model,
            choices=[choice],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
        )

    def _stream_chat_completion(
        self,
        completion_id: str,
        created_timestamp: int,
        model: str,
        content: Optional[str],
        tool_calls: Optional[List[ToolCall]],
        finish_reason: str,
    ) -> Iterator[ChatCompletionChunk]:
        """Generate stream events emitting initial role, content tokens, and finish reason."""
        yield ChatCompletionChunk(
            id=completion_id,
            object="chat.completion.chunk",
            created=created_timestamp,
            model=model,
            choices=[
                ChatCompletionChunkChoice(
                    index=0,
                    delta=ChatCompletionChunkDelta(role="assistant"),
                    finish_reason=None,
                )
            ],
        )

        if tool_calls:
            yield ChatCompletionChunk(
                id=completion_id,
                object="chat.completion.chunk",
                created=created_timestamp,
                model=model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(tool_calls=tool_calls),
                        finish_reason=None,
                    )
                ],
            )
        elif content:
            tokens = content.split(" ")
            for i, token in enumerate(tokens):
                token_text = token if i == 0 else f" {token}"
                yield ChatCompletionChunk(
                    id=completion_id,
                    object="chat.completion.chunk",
                    created=created_timestamp,
                    model=model,
                    choices=[
                        ChatCompletionChunkChoice(
                            index=0,
                            delta=ChatCompletionChunkDelta(content=token_text),
                            finish_reason=None,
                        )
                    ],
                )

        yield ChatCompletionChunk(
            id=completion_id,
            object="chat.completion.chunk",
            created=created_timestamp,
            model=model,
            choices=[
                ChatCompletionChunkChoice(
                    index=0,
                    delta=ChatCompletionChunkDelta(),
                    finish_reason=finish_reason,
                )
            ],
        )

    def create_completion(
        self,
        model: str,
        prompt: Union[str, List[str]],
        max_tokens: int = 16,
        temperature: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
    ) -> Completion:
        """Execute classic text completion on given prompt string."""
        prompt_text = prompt if isinstance(prompt, str) else " ".join(prompt)
        raw_completion = f"{prompt_text.strip()} generated continuation text for verification."

        finish_reason = "stop"
        stop_list: List[str] = [stop] if isinstance(stop, str) else (stop or [])
        for stop_token in stop_list:
            if stop_token in raw_completion:
                raw_completion = raw_completion.split(stop_token)[0]
                finish_reason = "stop"
                break

        words = raw_completion.split()
        if len(words) > max_tokens:
            raw_completion = " ".join(words[:max_tokens])
            finish_reason = "length"

        prompt_tokens = self.count_tokens(prompt_text)
        completion_tokens = self.count_tokens(raw_completion)

        return Completion(
            id=f"cmpl-{uuid.uuid4().hex[:12]}",
            object="text_completion",
            created=int(time.time()),
            model=model,
            choices=[CompletionChoice(text=raw_completion, index=0, finish_reason=finish_reason)],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )

    def create_embeddings(
        self,
        input_data: Union[str, List[str]],
        model: str = "text-embedding-3-small",
        dimensions: Optional[int] = None,
    ) -> EmbeddingResponse:
        """Generate L2-normalized deterministic embedding vectors using feature hashing."""
        if dimensions is not None:
            if dimensions <= 0:
                raise BadRequestError("Embedding dimension must be a positive integer.", status_code=400)
            target_dim = dimensions
        else:
            target_dim = 64

        inputs: List[str] = [input_data] if isinstance(input_data, str) else input_data
        embedding_objects: List[Embedding] = []
        total_tokens = 0

        for idx, text in enumerate(inputs):
            tokens = text.lower().strip().split()
            total_tokens += max(1, len(tokens))

            vector = [0.0] * target_dim

            for token in tokens:
                token_hash = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
                bucket = token_hash % target_dim
                sign = 1.0 if ((token_hash >> 8) & 1) == 1 else -1.0
                vector[bucket] += sign * (1.0 + len(token) * 0.1)

            if len(text) >= 3:
                for i in range(len(text) - 2):
                    trigram = text[i:i+3].lower()
                    tri_hash = int(hashlib.md5(trigram.encode("utf-8")).hexdigest(), 16)
                    bucket = tri_hash % target_dim
                    sign = 1.0 if ((tri_hash >> 4) & 1) == 1 else -1.0
                    vector[bucket] += sign * 0.5

            norm = math.sqrt(sum(v * v for v in vector))
            if norm == 0.0:
                vector[0] = 1.0
            else:
                vector = [round(v / norm, 8) for v in vector]

            embedding_objects.append(
                Embedding(
                    object="embedding",
                    embedding=vector,
                    index=idx,
                )
            )

        return EmbeddingResponse(
            object="list",
            data=embedding_objects,
            model=model,
            usage=Usage(
                prompt_tokens=total_tokens,
                completion_tokens=0,
                total_tokens=total_tokens,
            ),
        )
