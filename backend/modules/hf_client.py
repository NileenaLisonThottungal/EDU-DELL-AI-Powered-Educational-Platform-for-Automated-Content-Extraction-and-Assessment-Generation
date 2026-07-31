"""Thin wrapper around the Hugging Face Inference API (huggingface_hub.InferenceClient).

Centralized here so every module that needs the question-generation LLM / BERT /
Sentence-BERT goes through one client and one place to mock in tests.
"""
from huggingface_hub import InferenceClient

from config import Config

BERT_MASK_TOKEN = "[MASK]"

_client = None


def get_client() -> InferenceClient:
    global _client
    if _client is None:
        _client = InferenceClient(token=Config.HF_TOKEN or None)
    return _client


def generate_text(prompt: str, max_new_tokens: int = 64, model: str | None = None) -> str:
    """Chat-completion based question formation (Algorithm 1).

    The paper specifies FLAN-T5, but Hugging Face's Inference Providers no
    longer serve plain text2text-generation models like FLAN-T5 (only
    chat/instruct models are routed for text generation), so this uses an
    instruct model's chat-completion endpoint instead — same role in the
    pipeline (rewriting a sentence into a question).
    """
    client = get_client()
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model or Config.QUESTION_GEN_MODEL,
        max_tokens=max_new_tokens,
    )
    return (response.choices[0].message.content or "").strip()


def fill_mask(text_with_mask: str, model: str | None = None, top_k: int = 10) -> list[dict]:
    """BERT masked-word prediction — used for distractor support (Algorithm 1)."""
    client = get_client()
    return client.fill_mask(text_with_mask, model=model or Config.BERT_MASK_MODEL, top_k=top_k)


def embed(texts: list[str] | str, model: str | None = None):
    """Sentence-BERT embeddings — used for semantic filtering and storage.

    Accepts a single string (-> one vector) or a list of strings (-> list of vectors).
    """
    client = get_client()
    embed_model = model or Config.SENTENCE_EMBED_MODEL

    if isinstance(texts, str):
        vector = client.feature_extraction(texts, model=embed_model)
        return _as_flat_vector(vector)

    return [_as_flat_vector(client.feature_extraction(t, model=embed_model)) for t in texts]


def _as_flat_vector(raw):
    """Some models return per-token embeddings (2D); mean-pool down to one vector.

    Also casts every element to a native Python float — feature_extraction
    returns numpy float32 values, which ChromaDB's strict isinstance(x, float)
    validation rejects.
    """
    arr = raw
    # numpy arrays and nested lists both expose len()/indexing, so this works for either.
    if len(arr) and hasattr(arr[0], "__len__"):
        num_tokens = len(arr)
        dim = len(arr[0])
        return [float(sum(arr[t][d] for t in range(num_tokens)) / num_tokens) for d in range(dim)]
    return [float(x) for x in arr]
