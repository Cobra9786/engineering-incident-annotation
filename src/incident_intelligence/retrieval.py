from __future__ import annotations

from dataclasses import dataclass

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from .knowledge import KnowledgeDocument


DEFAULT_EMBEDDING_MODEL_ID = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


@dataclass(frozen=True)
class RetrievalResult:
    document_id: str
    title: str
    source_path: str
    text: str
    score: float


class SemanticKnowledgeRetriever:
    def __init__(
        self,
        documents: list[KnowledgeDocument],
        *,
        model_id: str = DEFAULT_EMBEDDING_MODEL_ID,
    ) -> None:
        if not documents:
            raise ValueError(
                "retriever requires at least one document"
            )

        self.documents = documents
        self.model_id = model_id
        self.model = SentenceTransformer(model_id)

        corpus_texts = [
            document.text
            for document in documents
        ]

        self.document_embeddings = self.model.encode(
            corpus_texts,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 3,
    ) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError(
                "retrieval query must not be empty"
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be at least 1"
            )

        query_embedding = self.model.encode(
            query,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

        similarities = cos_sim(
            query_embedding,
            self.document_embeddings,
        )[0]

        limit = min(top_k, len(self.documents))

        ranked_indices = similarities.argsort(
            descending=True
        )[:limit]

        results: list[RetrievalResult] = []

        for index_tensor in ranked_indices:
            index = int(index_tensor.item())
            document = self.documents[index]

            results.append(
                RetrievalResult(
                    document_id=document.document_id,
                    title=document.title,
                    source_path=document.source_path,
                    text=document.text,
                    score=float(similarities[index].item()),
                )
            )

        return results