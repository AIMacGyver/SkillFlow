"""Base skill contract with explicit Pydantic input and output models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, get_args, get_origin

from pydantic import BaseModel, ValidationError


class SkillContractError(Exception):
    """Raised when data cannot satisfy a skill's declared Pydantic contract.

    Args:
        message: Human-readable explanation of the mismatch.
    """

    def __init__(self, message: str) -> None:
        """Create a contract error.

        Args:
            message: Human-readable explanation of the mismatch.
        """
        super().__init__(message)


class Skill[InT: BaseModel, OutT: BaseModel](ABC):
    """A reusable unit of work with a typed Pydantic boundary.

    Subclasses declare models as ``Skill[InputModel, OutputModel]`` and implement
    ``run``. Skills may use any Python objects internally, but every public
    boundary must stay serializable through these models.

    Attributes:
        name: Stable identifier used in logs and contract errors.
    """

    _input_model: ClassVar[type[BaseModel] | None] = None
    _output_model: ClassVar[type[BaseModel] | None] = None

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Bind Input/Output models from the Skill[In, Out] type parameters."""
        super().__init_subclass__(**kwargs)
        for base in getattr(cls, "__orig_bases__", ()):
            origin = get_origin(base)
            if origin is Skill:
                args = get_args(base)
                if len(args) == 2:
                    cls._input_model = args[0]
                    cls._output_model = args[1]
                return

    @property
    def name(self) -> str:
        """Return the skill's public name."""
        return type(self).__name__

    @property
    def input_model(self) -> type[InT]:
        """Return the Pydantic model this skill accepts."""
        if self._input_model is None:
            raise SkillContractError(f"{self.name} did not declare Skill[Input, Output] models.")
        return self._input_model  # type: ignore[return-value]

    @property
    def output_model(self) -> type[OutT]:
        """Return the Pydantic model this skill produces."""
        if self._output_model is None:
            raise SkillContractError(f"{self.name} did not declare Skill[Input, Output] models.")
        return self._output_model  # type: ignore[return-value]

    def adapt_input(self, data: object) -> InT:
        """Coerce previous-step data into this skill's Input model.

        Args:
            data: A Pydantic model or mapping produced by an upstream skill.

        Returns:
            An instance of this skill's Input model.

        Raises:
            SkillContractError: If the payload cannot be validated as Input.
        """
        if isinstance(data, self.input_model):
            return data

        payload: object = data.model_dump() if isinstance(data, BaseModel) else data

        try:
            return self.input_model.model_validate(payload)
        except ValidationError as exc:
            expected = ", ".join(self.input_model.model_fields)
            received = _describe_payload(data)
            raise SkillContractError(
                f"{self.name} expected Input fields [{expected}] but received {received}: {exc}"
            ) from exc

    @abstractmethod
    def run(self, data: InT) -> OutT:
        """Execute the skill.

        Args:
            data: Validated input for this skill.

        Returns:
            A Pydantic Output model for the next skill or the caller.
        """


def _describe_payload(data: object) -> str:
    """Return a short description of an incoming contract payload."""
    if isinstance(data, BaseModel):
        fields = ", ".join(type(data).model_fields)
        return f"{type(data).__name__} fields [{fields}]"
    if isinstance(data, dict):
        keys = ", ".join(str(key) for key in data)
        return f"mapping keys [{keys}]"
    return type(data).__name__
