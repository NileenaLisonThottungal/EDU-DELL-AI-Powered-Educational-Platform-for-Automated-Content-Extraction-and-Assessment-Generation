"""ChromaDB-backed semantic storage (Section 3.4): document-level embeddings
for "related documents" search, and sentence-chunk embeddings for chatbot RAG.
"""
import chromadb

from config import Config
from modules.semantic.embeddings import embed_text, embed_texts

_client = None
_documents_collection = None
_chunks_collection = None

_PREVIEW_SENTENCE_COUNT = 5


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=Config.CHROMA_DIR)
    return _client


def _get_documents_collection():
    global _documents_collection
    if _documents_collection is None:
        _documents_collection = _get_client().get_or_create_collection("documents")
    return _documents_collection


def _get_chunks_collection():
    global _chunks_collection
    if _chunks_collection is None:
        _chunks_collection = _get_client().get_or_create_collection("chunks")
    return _chunks_collection


def store_document(document_id: str, filename: str, sentences: list[str]) -> str:
    """Embeds and stores a document's preview (for related-doc search) and its
    sentence chunks (for chatbot retrieval). Returns the preview text used."""
    preview = " ".join(sentences[:_PREVIEW_SENTENCE_COUNT])

    _get_documents_collection().upsert(
        ids=[document_id],
        embeddings=[embed_text(preview)],
        documents=[preview],
        metadatas=[{"filename": filename}],
    )

    if sentences:
        chunk_ids = [f"{document_id}::{i}" for i in range(len(sentences))]
        _get_chunks_collection().upsert(
            ids=chunk_ids,
            embeddings=embed_texts(sentences),
            documents=sentences,
            metadatas=[{"document_id": document_id} for _ in sentences],
        )

    return preview


def find_related_documents(document_id: str, top_k: int = 5) -> list[dict]:
    collection = _get_documents_collection()
    existing = collection.get(ids=[document_id], include=["embeddings"])
    if not existing["ids"]:
        return []

    results = collection.query(
        query_embeddings=[existing["embeddings"][0]],
        n_results=top_k + 1,
        include=["documents", "metadatas", "distances"],
    )

    related = []
    for doc_id, preview, metadata, distance in zip(
        results["ids"][0], results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        if doc_id == document_id:
            continue
        related.append(
            {
                "document_id": doc_id,
                "filename": metadata.get("filename", ""),
                "preview": preview,
                "similarity": max(0.0, 1 - distance),
            }
        )

    return related[:top_k]


def retrieve_relevant_chunks(document_id: str, query: str, top_k: int = 4) -> list[str]:
    collection = _get_chunks_collection()
    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=top_k,
        where={"document_id": document_id},
        include=["documents"],
    )
    if not results["documents"]:
        return []
    return results["documents"][0]
