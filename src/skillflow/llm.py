"""Thin LLM interface so skills stay independent of any provider."""

from typing import Protocol

from skillflow.types import ChatMessage


class LLMClient(Protocol):
    """Provider-agnostic chat completion client.

    Skills depend on this protocol, not a concrete SDK. Swap Ollama, a hosted
    OpenAI-compatible API, or a test stub without changing skill code.
    """

    def complete(self, messages: list[ChatMessage]) -> str:
        """Return the assistant text for a chat completion.

        Args:
            messages: Ordered chat turns to send to the model.

        Returns:
            The assistant message content.
        """
