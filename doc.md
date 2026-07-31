# EDU-DELL — Step-by-Step Build Plan

Status: **Built, tested, and verified end-to-end with real API keys (2026-07-30).**
Scope source: `Abstract.docx` (paper) + `images/1.jpg`–`8.jpg` (UI reference) + your decisions below.

**Post-build model substitution**: once real API keys were tested, both
FLAN-T5 and `gemini-1.5-flash` turned out to have been retired from their
respective hosted APIs since this plan was written (Hugging Face's Inference
Providers no longer serve plain text2text-generation models for text
generation; Google retired the Gemini 1.5 line). `Qwen/Qwen2.5-7B-Instruct`
and `gemini-flash-latest` now fill those roles — see the README's "Note on
models" for details. Everything below describing FLAN-T5/Gemini 1.5 Flash
reflects the original plan; the running code uses the replacements.

Decisions locked in from our discussion:
- **Models**: Hybrid — Hugging Face models power MCQ / Fill-in-the-Blank / True-False generation (as in the paper). Google Gemini 1.5 Flash powers Summarization and the Chatbot (as in the paper).
- **HF inference mode**: Hugging Face **Inference API** (hosted), not local weights. Requires an `HF_TOKEN`.
- Also required: a **Gemini API key** (`GEMINI_API_KEY`) for summarization + chat.

If you don't have these two keys yet, get them from huggingface.co/settings/tokens and aistudio.google.com/apikey — implementation can start in parallel, they're only needed to actually run the app.

---

## 1. What we're building

A full-stack educational AI platform, **EDU-DELL**:

- Upload a document (PDF / DOCX / PPTX / TXT) or paste a URL / raw text.
- Get an AI summary (Gemini) and a chatbot you can ask about the document (Gemini + semantic retrieval).
- Auto-generate three assessment types from the content: **MCQs**, **Fill-in-the-Blank**, **True/False**.
- Take the quiz in-app, get scored, see correct answers + explanations.
- Documents are embedded and stored so the system can recommend/relate similar past documents.

Backend: **Python / Flask** (matches the paper: "deployed as a Flask web application").
Frontend: **React**.

---

## 2. Architecture

```
                        ┌─────────────────────────┐
                        │        React SPA        │
                        │  Upload · Quiz · Chat ·  │
                        │  Summary · Results       │
                        └───────────┬─────────────┘
                                    │ REST (JSON) / fetch
                        ┌───────────▼─────────────┐
                        │        Flask API        │
                        ├──────────────────────────┤
        ┌───────────────┤ 1. Input Layer           │
        │               │ 2. Preprocessing Engine  │
        │               │ 3. Question Generation   │
        │               │ 4. Semantic Storage      │
        │               │ 5. Chatbot Layer         │
        │               └──────────────────────────┘
        │
   ┌────▼─────┐   ┌──────────────┐   ┌───────────────┐   ┌────────────────┐
   │ Extractors│   │ spaCy (local)│   │ HF Inference  │   │ Gemini 1.5     │
   │ PDF/DOCX/ │   │ WordNet(nltk)│   │ API: FLAN-T5, │   │ Flash API:     │
   │ PPTX/URL  │   │ (rule-based  │   │ BERT-mask,    │   │ Summarization  │
   │           │   │  FIB & T/F)  │   │ Sentence-BERT │   │ + Chat         │
   └───────────┘   └──────────────┘   └───────┬───────┘   └───────┬────────┘
                                               │                   │
                                        ┌──────▼───────────────────▼──────┐
                                        │   ChromaDB (local persistent)   │
                                        │   document embeddings + chunks  │
                                        └──────────────────────────────────┘
```

This maps directly onto the paper's five modules (Input Layer → Preprocessing Engine → Question Generation Module → Semantic Storage → Chatbot Layer, Section "Architecture Overview").

---

## 3. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend framework | Flask + flask-cors | Matches paper ("Flask web application") |
| PDF extraction | `pdfplumber` (+ `PyPDF2` fallback) | Paper cites PyPDF2/pdfminer |
| DOCX extraction | `python-docx` | Paper cites python-docx |
| PPTX extraction | `python-pptx` | Paper cites python-pptx |
| URL extraction | `requests` + `BeautifulSoup4` | Paper cites BeautifulSoup |
| NLP pipeline | `spaCy` (`en_core_web_sm`) | Sentence segmentation, keyword/POS extraction — runs locally (not an LLM call) |
| Synonyms/antonyms | `nltk` WordNet | Distractor & false-statement generation |
| MCQ question formation | HF Inference API — `google/flan-t5-large` | Paper: FLAN-T5 for question generation |
| Distractor support | HF Inference API — `bert-base-uncased` (fill-mask) | Paper: BERT masked-word prediction |
| Semantic filtering / embeddings | HF Inference API — `sentence-transformers/all-MiniLM-L6-v2` (feature-extraction) | Paper: Sentence-BERT |
| Vector store | `chromadb` (local persistent client) | Paper: ChromaDB |
| Summarization | Gemini 1.5 Flash (`google-generativeai`) | Paper: Gemini-powered summarization |
| Chatbot | Gemini 1.5 Flash + ChromaDB retrieval (RAG) | Paper: Chatbot Layer |
| Grammar scoring (eval) | `language_tool_python` | Needed for the "Grammar Check" metric in Table 1/2 |
| ROUGE scoring (eval) | `rouge-score` | Needed for `rougeL` metric in Table 2 |
| Frontend | React (Vite) + Tailwind CSS | Fast dev loop, matches component-heavy UI in the reference images |
| Frontend HTTP | `fetch` / `axios` | — |
| Testing (backend) | `pytest` + `pytest-mock` (HF/Gemini calls mocked — no network/keys needed to run the suite) | Deterministic, CI-friendly |
| Testing (frontend) | `vitest` + `@testing-library/react` | Component-level tests for quiz flows |
| PDF export | `xhtml2pdf` (pure-Python HTML→PDF, backend) | Renders quiz/results from the same template data as the UI, no headless-browser dependency |
| Attempt storage | SQLite via `sqlite3`/SQLAlchemy, keyed by session id | Lightweight, no auth needed, persists score history across visits |
| Theming | CSS variables + Tailwind `dark:` variants, toggled via a React context + `localStorage` | Single design system, both light and dark, no page-specific styles |

---

## 4. Backend module layout

```
backend/
  app.py                        # Flask app + all route registration
  config.py                     # env vars: HF_TOKEN, GEMINI_API_KEY, CHROMA_DIR, ATTEMPTS_DB
  requirements.txt
  pytest.ini
  modules/
    hf_client.py                # shared HF Inference API wrapper (FLAN-T5, BERT fill-mask, Sentence-BERT)
    gemini_client.py             # shared Gemini client
    nlp_pipeline.py               # shared spaCy singleton
    similarity.py                 # cosine similarity helper
    quiz_grading.py               # scores a submitted attempt against stored answers
    extraction/
      pdf_extractor.py
      docx_extractor.py
      pptx_extractor.py
      txt_extractor.py
      url_extractor.py             # includes SSRF guard (blocks private/loopback hosts)
      __init__.py                  # extract_from_file/url/raw_text dispatcher
    preprocessing/
      cleaner.py                   # symbol/noise removal, normalization
      segmenter.py                 # spaCy sentence segmentation + filtering rules (Section 3.2.2)
    question_generation/
      keyword_extractor.py         # spaCy noun/proper-noun keyword extraction
      distractors.py               # BERT fill-mask + WordNet synonyms + Sentence-BERT filtering, difficulty bands
      mcq_generator.py             # Algorithm 1
      fib_generator.py             # Algorithm 2
      tf_generator.py              # Algorithm 3 (WordNet antonyms)
    semantic/
      embeddings.py                # HF Inference API client (feature-extraction)
      chroma_store.py              # document-level + chunk-level embeddings in ChromaDB
    summarization/
      summarizer.py                # Gemini call
    chatbot/
      chat_service.py              # retrieve top-k from Chroma -> build prompt -> Gemini
    evaluation/
      metrics.py                   # coherence, distractor diversity/similarity, grammar, balance, rougeL
    storage/                       # SQLite persistence (renamed from the earlier "attempts" package
                                    # once it grew to also hold documents/quizzes, not just attempts)
      db.py                        # schema + connection helper
      documents_store.py           # uploaded documents (raw text, sentences, cached summary)
      quiz_store.py                # generated quizzes (questions + correct answers)
      attempts_store.py            # score history per session id
    export/
      pdf_export.py                # HTML template -> xhtml2pdf -> PDF (quiz or results)
      templates/
        quiz.html
        results.html
  tests/
    conftest.py                    # mocks HF/Gemini, isolates SQLite+Chroma per test, Flask test client
    test_extraction.py
    test_preprocessing.py
    test_mcq_generator.py
    test_fib_generator.py
    test_tf_generator.py
    test_semantic_storage.py
    test_summarizer.py             # Gemini call mocked
    test_chatbot.py                # Gemini + Chroma mocked
    test_attempts.py               # quiz + score history persistence
    test_pdf_export.py             # PDF generation produces valid, non-empty output
    test_api_routes.py             # end-to-end route tests, all external calls mocked
```

## 5. Frontend page layout (mapped to your reference images, refined)

| Screen | Reference | Notes / improvements |
|---|---|---|
| **Upload / Home** | `1.jpg` | Keep the clean centered-card layout; add drag-and-drop (like `6.jpg`'s dropzone) in addition to the file picker; support URL + raw-text tabs, not just file upload. |
| **Document Workspace** | `6.jpg`, `7.jpg`, `8.jpg` | Combine into one screen after upload: left = uploaded doc + summary; right = chat panel; bottom = related documents ("Get Recommendations"). Kept dark theme from these images since it reads well for a workspace/dashboard screen. |
| **MCQ Quiz** | `2.jpg` | Keep numbered question + 4 clickable option rows; add a progress bar and a running "answered X/Y" indicator (not in original). |
| **Fill in the Blanks** | `3.jpg` | Keep sentence-with-blank + text input; add inline validation state (answered/unanswered) before submit. |
| **True/False** | `4.jpg` | Keep statement + True/False buttons; add visual selected-state highlighting. |
| **Results** | `5.jpg` | Keep per-question correct-answer + explanation layout; add a top summary card (score %, per-type breakdown chart) plus a **"Progress over time"** chart pulled from attempt history; "Download PDF" button on this screen. |

Overall style direction: unify the two visual styles from your images (light teal quiz cards vs. dark dashboard workspace) into one consistent design system — single color palette, shared typography/spacing, with a **light/dark theme toggle** in the app header so every screen renders in both modes, rather than one screen being permanently dark and another permanently light. Component reuse: one `QuestionCard` shell for MCQ/FIB/TF with type-specific answer inputs slotted in.

Additional UI elements from the approved extras:
- **MCQ generation options**: an Easy/Medium/Hard difficulty selector shown before generating an MCQ set (Upload or Document Workspace screen).
- **Results screen**: "Download PDF" button (results) and a "Download PDF" option on the pre-quiz screen (quiz questions only, no answers).
- **History screen** (new, small addition): a simple list/chart of past attempts for the current browser session, linked from the header/nav.

## 6. Core algorithms (implementing the paper's Algorithms 1–3)

- **MCQ** (`mcq_generator.py`): clean/segment text → extract keyword per sentence (spaCy) → generate distractors (BERT fill-mask + WordNet synonyms, filtered by Sentence-BERT similarity so distractors are "neither too easy nor too difficult") → form question via FLAN-T5 (blank the keyword) → shuffle 1 correct + 3 distractors → validate (non-empty, no duplicate options) → store.
- **FIB** (`fib_generator.py`): clean/segment → select keyword (noun/proper-noun, stopwords removed) → blank first occurrence only → validate → store.
- **True/False** (`tf_generator.py`): clean/segment → extract keyword → randomly choose True/keep-as-is or False/replace keyword with a WordNet antonym (fallback: generic incorrect term) → store with correct label.

## 7. Evaluation metrics (to reproduce Tables 1–5 from the paper)

Implemented in `evaluation/metrics.py`, computed automatically per generation batch and exposed via an admin/debug endpoint (not required for the quiz UX, but needed so the README can report real numbers instead of copying the paper's):

- MCQ: Question Coherence, Distractor Diversity, Distractor Similarity, Grammar Check, MCQ Balance.
- FIB: Keyword Importance, Sentence Coherence, Answer Predictability.
- T/F: Statement Coherence, False Statement Plausibility, Answer Predictability.
- Summarization / Chatbot: Coherence, Grammar, Coverage, ROUGE-L, Semantic Similarity.

## 8. API endpoints (draft)

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/documents` | Upload file / URL / raw text → extract, preprocess, embed, store in Chroma |
| GET | `/api/documents` | List uploaded documents |
| GET | `/api/documents/:id/summary` | Gemini summary of a document |
| GET | `/api/documents/:id/related` | ChromaDB similarity search → related docs |
| POST | `/api/documents/:id/chat` | Chat turn (RAG via Chroma + Gemini) |
| POST | `/api/documents/:id/quiz/mcq` | Generate MCQs (body includes `difficulty`: easy/medium/hard) |
| POST | `/api/documents/:id/quiz/fib` | Generate FIB questions |
| POST | `/api/documents/:id/quiz/tf` | Generate T/F questions |
| POST | `/api/quiz/:quizId/submit` | Submit answers → score + explanations; persists an attempt record for the session |
| GET | `/api/sessions/:sessionId/attempts` | Score history for the "Progress over time" chart |
| GET | `/api/quiz/:quizId/export.pdf` | Download the quiz (questions only) as PDF |
| GET | `/api/quiz/:quizId/results/:attemptId/export.pdf` | Download the results (score + explanations) as PDF |

## 9. Testing plan

- Unit tests per extractor, per generator, per metric function.
- All HF Inference API and Gemini API calls mocked in tests (`pytest-mock`) — the suite runs green with **no real API keys**, keeping CI deterministic and free.
- One end-to-end integration test per quiz type: sample text → full pipeline → assert well-formed output (correct option count, non-duplicate distractors, valid blank markers, valid T/F labels).
- Frontend: component tests for each quiz screen (answer selection, submit, results rendering) with a mocked API layer.

## 10. README plan

Overview & features · architecture diagram · tech stack · setup (Python venv + `requirements.txt`, spaCy model download, NLTK WordNet download, Node install, `.env` for `HF_TOKEN`/`GEMINI_API_KEY`) · running the app (backend + frontend dev servers) · running tests · API reference · evaluation results table · screenshots · future scope (kept from the paper: multilingual support, teacher dashboard, OCR/speech input, gamification) · license.

## 11. Extras (approved — added to scope)

- [x] **Score history / attempt tracking** — per-session (no auth), stored server-side keyed by a browser-generated session id (cookie or localStorage token). Results screen gets a "Progress over time" chart (score % per attempt).
- [x] **PDF export** — export a generated quiz (questions only) or the results page (score + explanations) to PDF. Backend-rendered (`xhtml2pdf`, pure Python, from an HTML template) so it matches the on-screen layout exactly, exposed as a download endpoint.
- [x] **Difficulty toggle for MCQ** — Easy/Medium/Hard control at generation time, implemented by filtering distractors by Sentence-BERT similarity band to the correct answer (Easy = low similarity/obviously wrong distractors, Hard = high similarity/close distractors).
- [x] **Light/dark theme switch** — global toggle in the app header; both the quiz screens and the document workspace get a consistent light and dark variant instead of being locked to one look each.

Anything from the paper's own "Future Scope" (multilingual, teacher dashboard, OCR/speech, mobile app, gamification) remains out-of-scope for v1 and is documented in the README as future work.

## 12. Build order

1. Backend skeleton: Flask app, config, extraction + preprocessing modules, tests for both.
2. Question generation modules (MCQ with difficulty bands, FIB, T/F) + distractor logic, tests.
3. Semantic storage (Chroma + embeddings) + summarization + chatbot, tests (mocked).
4. Attempts store (SQLite) + PDF export module, tests.
5. API routes wiring it all together, integration tests.
6. React app: theming (light/dark) + Upload → Document Workspace → Quiz screens (with difficulty selector) → Results (with progress chart + PDF download) → History screen, styled per Section 5.
7. Wire frontend to backend, manual end-to-end pass.
8. README + final test pass.

---

**Plan approved with all four extras included (score history, PDF export, MCQ difficulty toggle, light/dark theme). Ready to start building unless you have further changes.**
