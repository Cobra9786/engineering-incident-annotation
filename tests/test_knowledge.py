from pathlib import Path

import pytest

from incident_intelligence.knowledge import (
    load_knowledge_documents,
)


def test_load_knowledge_documents(
    tmp_path: Path,
) -> None:
    document = tmp_path / "pump.md"
    document.write_text(
        "# Pump Guidance\n\nInspect the pump.",
        encoding="utf-8",
    )

    documents = load_knowledge_documents(tmp_path)

    assert len(documents) == 1
    assert documents[0].document_id == "pump"
    assert documents[0].title == "Pump Guidance"


def test_empty_knowledge_document_is_rejected(
    tmp_path: Path,
) -> None:
    document = tmp_path / "empty.md"
    document.write_text("", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="empty",
    ):
        load_knowledge_documents(tmp_path)


def test_missing_knowledge_directory_is_rejected(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        load_knowledge_documents(missing)