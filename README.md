# Testing-Repo-for-Grantfox
Just for testing
Esto es una prueba

Esto es una contribucion en grantfox

test final

## OpenAI Client Package

This repository provides an OpenAI API-compatible Python client and offline execution engine (`openai`), implemented using only Python standard library modules with zero third-party dependencies.

### Features

- **Standard API Surface**: Full compatibility with `client.chat.completions.create`, `client.completions.create`, `client.embeddings.create`, and `client.models`.
- **Offline / Local Engine**: Execute chat completions, deterministic token counting, embeddings, and model queries without external network requests or API keys (`local_backend=True`).
- **HTTP Transport**: Built-in `urllib`-based transport for sending live requests to OpenAI-compatible endpoints with authorization headers and streaming support.
- **Streaming Responses**: Real-time event streaming generating incremental `ChatCompletionChunk` tokens.
- **Function / Tool Calling**: Declarative tool schema support with automatic parameter extraction and `finish_reason="tool_calls"`.
- **L2-Normalized Embeddings**: Deterministic feature hashing yielding unit-norm vector representations (Euclidean norm = 1.0) with semantic similarity preservation.

### Quick Start

#### Chat Completions

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are an AI assistant."},
        {"role": "user", "content": "Who are you?"}
    ]
)

print(response.choices[0].message.content)
```

#### Streaming Completions

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Explain machine learning."}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

#### Embeddings

```python
from openai import OpenAI

client = OpenAI()

response = client.embeddings.create(
    input=["artificial intelligence", "machine learning"],
    model="text-embedding-3-small",
    dimensions=64
)

for item in response.data:
    print(f"Index: {item.index}, Dimension: {len(item.embedding)}")
```

### Running Tests

Execute the unmocked unit test suite using standard Python `unittest`:

```bash
python3 -m unittest discover tests
```
