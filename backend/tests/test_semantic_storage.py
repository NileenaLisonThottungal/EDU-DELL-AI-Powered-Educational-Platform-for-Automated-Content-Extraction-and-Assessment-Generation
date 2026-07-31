from modules.semantic import find_related_documents, retrieve_relevant_chunks, store_document


def test_store_and_retrieve_relevant_chunks():
    store_document("doc-1", "notes.txt", ["Replication enables horizontal scaling.", "Consistency matters."])
    chunks = retrieve_relevant_chunks("doc-1", "scaling", top_k=2)
    assert chunks  # at least one chunk retrieved
    assert any("Replication" in c or "Consistency" in c for c in chunks)


def test_find_related_documents_excludes_self():
    store_document("doc-a", "a.txt", ["Vector databases store embeddings for search."])
    store_document("doc-b", "b.txt", ["ChromaDB is a vector database used for retrieval."])

    related = find_related_documents("doc-a", top_k=5)
    related_ids = [r["document_id"] for r in related]

    assert "doc-a" not in related_ids
    assert "doc-b" in related_ids


def test_find_related_documents_unknown_document_returns_empty():
    assert find_related_documents("does-not-exist") == []
