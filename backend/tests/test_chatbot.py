from modules.chatbot import answer_question
from modules.semantic import store_document


def test_answer_question_uses_retrieved_context():
    store_document("doc-chat", "notes.txt", ["ChromaDB stores embeddings for semantic search."])
    answer = answer_question("doc-chat", "What does ChromaDB store?")
    assert answer
    assert "mocked Gemini response" in answer


def test_answer_question_with_conversation_history():
    store_document("doc-chat-2", "notes.txt", ["Sentence transformers create dense embeddings."])
    history = [{"role": "user", "content": "What is this document about?"}, {"role": "assistant", "content": "Embeddings."}]
    answer = answer_question("doc-chat-2", "Tell me more.", history=history)
    assert answer
