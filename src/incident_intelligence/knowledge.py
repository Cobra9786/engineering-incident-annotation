from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeDocument:
    document_id: str
    title: str
    source_path: str
    text: str


def load_knowledge_documents(
    directory: Path,
) -> list[KnowledgeDocument]:
    if not directory.exists():
        raise FileNotFoundError(
            f"knowledge directory does not exist: {directory}"
        )

    documents: list[KnowledgeDocument] = []

    for path in sorted(directory.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()

        if not text:
            raise ValueError(
                f"knowledge document is empty: {path}"
            )

        first_line = text.splitlines()[0].strip()
        title = first_line.removeprefix("#").strip()

        documents.append(
            KnowledgeDocument(
                document_id=path.stem,
                title=title,
                source_path=str(path),
                text=text,
            )
        )

    if not documents:
        raise ValueError(
            f"no Markdown documents found in {directory}"
        )

    return documents