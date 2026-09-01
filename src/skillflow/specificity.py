"""Load task-specific instructions from files outside skill code."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

TEXT_SUFFIXES = {".md", ".txt"}
MAPPING_SUFFIXES = {".yaml", ".yml"}


class SpecificityError(Exception):
    """Raised when a specificity file is missing or has an unsupported format.

    Args:
        message: Human-readable explanation of the load failure.
    """

    def __init__(self, message: str) -> None:
        """Create a specificity load error.

        Args:
            message: Human-readable explanation of the load failure.
        """
        super().__init__(message)


def load_specificity(path: str | Path) -> str | dict[str, Any]:
    """Load specificity from a text or YAML file.

    Markdown and plain-text files return their contents as a string. YAML files
    return a mapping. Task-specific prompts belong here so skills stay stable.

    Args:
        path: Path to a ``.md``, ``.txt``, ``.yaml``, or ``.yml`` file.

    Returns:
        The file contents as text or a YAML mapping.

    Raises:
        SpecificityError: If the file is missing, empty in an unexpected way,
            or uses an unsupported suffix.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise SpecificityError(f"Specificity file not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        return file_path.read_text(encoding="utf-8")
    if suffix in MAPPING_SUFFIXES:
        loaded = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        if loaded is None:
            return {}
        if not isinstance(loaded, dict):
            raise SpecificityError(f"YAML specificity must be a mapping, got {type(loaded).__name__}: {file_path}")
        return loaded

    raise SpecificityError(
        f"Unsupported specificity file type '{file_path.suffix}'. "
        f"Use one of: {', '.join(sorted(TEXT_SUFFIXES | MAPPING_SUFFIXES))}"
    )
