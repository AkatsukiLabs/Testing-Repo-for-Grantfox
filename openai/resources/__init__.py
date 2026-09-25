"""Resource endpoints for the OpenAI client API."""

from openai.resources.chat import Chat
from openai.resources.completions import Completions
from openai.resources.embeddings import Embeddings
from openai.resources.models import Models

__all__ = ["Chat", "Completions", "Embeddings", "Models"]
