"""Thin LLM interface so skills stay independent of any provider."""

from __future__ import annotations

import os
from typing import Protocol

from openai import OpenAI

from skillflow.types import ChatMessage

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_API_KEY = "ollama"
DEFAULT_MODEL = "qwen3:8b"


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


class OpenAICompatibleClient:
    """Chat client for Ollama or any OpenAI-compatible HTTP endpoint.

    Defaults target a local Ollama server. Point ``SKILLFLOW_LLM_BASE_URL`` at a
    hosted provider later without changing skills.

    Args:
        base_url: API root, including ``/v1``.
        api_key: API key. Ollama ignores this but the OpenAI SDK requires a value.
        model: Model name, for example ``qwen3:8b``.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        """Create a client from arguments or SkillFlow environment variables.

        Args:
            base_url: API root, including ``/v1``.
            api_key: API key. Ollama ignores this but the OpenAI SDK requires a value.
            model: Model name, for example ``qwen3:8b``.
        """
        self.base_url = base_url or os.getenv("SKILLFLOW_LLM_BASE_URL", DEFAULT_BASE_URL)
        self.api_key = api_key or os.getenv("SKILLFLOW_LLM_API_KEY", DEFAULT_API_KEY)
        self.model = model or os.getenv("SKILLFLOW_LLM_MODEL", DEFAULT_MODEL)
        self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def complete(self, messages: list[ChatMessage]) -> str:
        """Return the assistant text for a chat completion.

        Args:
            messages: Ordered chat turns to send to the model.

        Returns:
            The assistant message content.

        Raises:
            RuntimeError: If the model returns an empty message.
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": message.role, "content": message.content} for message in messages],
            extra_body={"think": False},
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError(f"Model '{self.model}' returned an empty completion.")
        return content.strip()


class StubLLMClient:
    """Deterministic LLM stand-in for tests and offline recipe checks.

    Args:
        responses: Optional queue of replies returned in order.
        default: Reply used after the queue is exhausted.
    """

    def __init__(self, responses: list[str] | None = None, default: str = "stub response") -> None:
        """Create a stub client.

        Args:
            responses: Optional queue of replies returned in order.
            default: Reply used after the queue is exhausted.
        """
        self._responses = list(responses or [])
        self._default = default

    def complete(self, messages: list[ChatMessage]) -> str:
        """Return the next queued reply, or the default string.

        Args:
            messages: Chat turns. Ignored except to satisfy the protocol.

        Returns:
            A canned assistant string.
        """
        del messages
        if self._responses:
            return self._responses.pop(0)
        return self._default
