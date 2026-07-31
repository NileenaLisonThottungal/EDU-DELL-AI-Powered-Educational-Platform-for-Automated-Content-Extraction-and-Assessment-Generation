"""Chatbot Layer (Section 3.1.5 / 3.5): semantic retrieval over ChromaDB +
Gemini 1.5 Flash for grounded, document-aware answers."""
from modules import gemini_client
from modules.semantic import retrieve_relevant_chunks

_CHAT_PROMPT = (
    "You are an educational assistant answering questions about a document the "
    "user uploaded. Use only the context below to answer; if the answer isn't in "
    "the context, say you're not sure.\n\n"
    "Context:\n{context}\n\n"
    "{history}"
    "User question: {question}\n"
    "Answer concisely:"
)


def _format_history(history: list[dict]) -> str:
    if not history:
        return ""
    lines = [f"{turn['role'].capitalize()}: {turn['content']}" for turn in history]
    return "Conversation so far:\n" + "\n".join(lines) + "\n\n"


def answer_question(document_id: str, question: str, history: list[dict] | None = None) -> str:
    chunks = retrieve_relevant_chunks(document_id, question)
    context = "\n---\n".join(chunks) if chunks else "(no matching context found)"

    prompt = _CHAT_PROMPT.format(
        context=context,
        history=_format_history(history or []),
        question=question,
    )
    return gemini_client.generate(prompt)
