"""Behavior tests for loading external specificity files."""

from pathlib import Path

import pytest

from skillflow import SpecificityError, load_specificity


def test_load_markdown_specificity(tmp_path: Path) -> None:
    path = tmp_path / "extract.md"
    path.write_text("Use short bullets.\n", encoding="utf-8")

    loaded = load_specificity(path)

    assert loaded == "Use short bullets.\n"


def test_load_yaml_specificity(tmp_path: Path) -> None:
    path = tmp_path / "style.yaml"
    path.write_text("tone: concise\nmax_bullets: 5\n", encoding="utf-8")

    loaded = load_specificity(path)

    assert loaded == {"tone": "concise", "max_bullets": 5}


def test_missing_specificity_fails_fast(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"

    with pytest.raises(SpecificityError, match="not found"):
        load_specificity(missing)


def test_unsupported_specificity_type_fails_fast(tmp_path: Path) -> None:
    path = tmp_path / "notes.json"
    path.write_text('{"tone": "casual"}', encoding="utf-8")

    with pytest.raises(SpecificityError, match="Unsupported specificity file type"):
        load_specificity(path)


def test_yaml_must_be_a_mapping(tmp_path: Path) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- one\n- two\n", encoding="utf-8")

    with pytest.raises(SpecificityError, match="must be a mapping"):
        load_specificity(path)
