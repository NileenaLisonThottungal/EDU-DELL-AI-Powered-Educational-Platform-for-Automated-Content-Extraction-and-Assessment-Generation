import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    HF_TOKEN = os.environ.get("HF_TOKEN", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

    CHROMA_DIR = os.environ.get("CHROMA_DIR", os.path.join(BASE_DIR, "chroma_data"))
    ATTEMPTS_DB = os.environ.get("ATTEMPTS_DB", os.path.join(BASE_DIR, "attempts.db"))

    # HF Inference API model ids.
    # The paper specifies FLAN-T5 for question formation, but Hugging Face's
    # current Inference Providers only route text-generation to chat/instruct
    # models, not plain text2text-generation models like FLAN-T5 — so an
    # instruct model is used instead (see modules/hf_client.py).
    QUESTION_GEN_MODEL = os.environ.get("QUESTION_GEN_MODEL", "Qwen/Qwen2.5-7B-Instruct")
    # Bare model names (e.g. "bert-base-uncased") no longer resolve via the
    # Inference Providers router — the fully-qualified namespaced id is required.
    BERT_MASK_MODEL = os.environ.get("BERT_MASK_MODEL", "google-bert/bert-base-uncased")
    SENTENCE_EMBED_MODEL = os.environ.get(
        "SENTENCE_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    # "gemini-flash-latest" is an alias Google keeps pointed at their current
    # recommended flash model, so this doesn't go stale like a pinned version
    # (e.g. "gemini-1.5-flash", specified in the paper, has since been retired).
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

    MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "20"))
