# EDU-DELL

EDU-DELL is an AI-powered educational platform that turns any document, web
page, or pasted text into a summary, a document-grounded chatbot, and
auto-generated Multiple-Choice, Fill-in-the-Blank, and True/False quizzes —
with score history, PDF export, and a light/dark UI.

## Publication

This project is the reference implementation of a peer-reviewed book chapter:

> **EDU-DELL: An AI-Powered Educational Platform for Automated Content Extraction and Assessment Generation**
> Nileena Lison, Liyan Grace Shaji, K. S. Lakshmi
> In: *Smart Trends in Computing and Communications* (Proceedings of SmartCom 2026),
> eds. Tomonobu Senjyu, Mufti Mahmud, Amit Joshi.
> Lecture Notes in Networks and Systems, vol. 1997. Springer, Cham, pp. 220–234.
> Published 10 July 2026.
> DOI: [10.1007/978-3-032-27563-9_21](https://doi.org/10.1007/978-3-032-27563-9_21)


The paper's architecture, algorithms (Sections 3.1–3.5), and evaluation
methodology (Tables 1–5) are implemented end-to-end in this repository — see
[doc.md](doc.md) for the module-by-module mapping from paper to code, and
[Evaluation metrics](#evaluation-metrics) below for how each reported metric
is reproduced as a real, computed value rather than a hardcoded number.

## Features

- **Multi-format ingestion**: PDF, DOCX, PPTX, TXT, a URL, or pasted text.
- **Summarization**: Gemini summarizes the uploaded document.
- **Document chatbot**: ask questions about the document; answers are
  grounded via semantic retrieval (Sentence-BERT + ChromaDB) over the
  document's own content, then answered by Gemini.
- **Quiz generation**:
  - **MCQ** — an instruct LLM forms the question, BERT (masked-word
    prediction) + WordNet generate distractors, filtered by Sentence-BERT
    similarity into an **Easy / Medium / Hard** difficulty band.
  - **Fill-in-the-Blank** — pure spaCy/rule-based, no LLM call.
  - **True/False** — pure spaCy + WordNet antonyms, no LLM call.
- **Related documents**: semantic similarity search across everything you've
  uploaded, via ChromaDB.
- **Score history**: every submitted attempt is saved per browser session (no
  login) and charted on the Results and History pages.
- **PDF export**: download a generated quiz (questions only) or a completed
  results page.
- **Light/dark theme** toggle across the whole app.

## Screenshots and test cases

Every screen and flow below was captured from a real, running instance —
live Gemini summarization/chat, live Hugging Face MCQ generation, real
ChromaDB similarity search — not mocked for the screenshots. Source files
used: [`sample_files/`](sample_files/) (a "Photosynthesis and Plant Biology"
document plus two topically related documents and one unrelated control
document, all generated for this test pass).

### 1. Upload — all three input methods

| File upload | URL input | Paste text |
|---|---|---|
| ![Upload file tab](screenshots/01-upload-file-tab.png) | ![Upload URL tab](screenshots/02-upload-url-tab.png) | ![Upload text tab](screenshots/03-upload-text-tab.png) |

File picked and ready to submit:

![File selected](screenshots/04-upload-file-selected.png)

### 2. Document Workspace — summary, chat, related documents

| Live Gemini summary | Live Gemini chat (RAG-grounded) |
|---|---|
| ![Workspace summary](screenshots/05-workspace-summary.png) | ![Workspace chat](screenshots/06-workspace-chat.png) |

Related documents via real ChromaDB semantic similarity search — correctly
surfaces the two biology-related documents over the unrelated Roman-history
control document:

![Related documents](screenshots/07-workspace-related-documents.png)

### 3. Fill-in-the-Blank quiz (no LLM call — pure spaCy)

| Generated questions | Answered | Scored results |
|---|---|---|
| ![FIB questions](screenshots/09-fib-quiz-questions.png) | ![FIB answered](screenshots/10-fib-quiz-answered.png) | ![FIB results](screenshots/11-fib-results.png) |

### 4. True/False quiz (no LLM call — spaCy + WordNet antonyms)

| Generated questions | Scored results |
|---|---|
| ![TF questions](screenshots/12-tf-quiz-questions.png) | ![TF results](screenshots/13-tf-results.png) |

### 5. Multiple-Choice quiz (Hugging Face: instruct LLM + BERT + WordNet, Hard difficulty)

| Difficulty selected | Generated questions | Answered | Scored results |
|---|---|---|---|
| ![MCQ difficulty](screenshots/14-workspace-mcq-hard-selected.png) | ![MCQ questions](screenshots/15-mcq-quiz-questions.png) | ![MCQ answered](screenshots/16-mcq-quiz-answered.png) | ![MCQ results](screenshots/17-mcq-results.png) |

### 6. Score history

![History page](screenshots/18-history-page.png)

### 7. Light/dark theme

| Dark — History | Dark — Workspace |
|---|---|
| ![History dark](screenshots/19-history-page-dark.png) | ![Workspace dark](screenshots/20-workspace-dark.png) |

(All other screenshots above were captured in light mode — the toggle
applies the same design system across every screen shown.)

### 8. PDF export

Both PDF endpoints were exercised for real; the generated files are checked
into [`screenshots/`](screenshots/) so you can inspect the actual output:

- [`sample_quiz_export.pdf`](screenshots/sample_quiz_export.pdf) — questions-only export, downloaded from a Fill-in-the-Blank quiz before submitting
- [`sample_results_export.pdf`](screenshots/sample_results_export.pdf) — scored results export, downloaded after submitting

### Automated test cases

Beyond the manual pass above, the codebase has 58 automated test cases that
run without any API keys (every Hugging Face / Gemini call is mocked):

| Suite | Count | Covers |
|---|---|---|
| `backend/tests/test_extraction.py` | 9 | PDF/DOCX/PPTX/TXT parsing, URL SSRF guard, unsupported-type handling |
| `backend/tests/test_preprocessing.py` | 5 | Noise/bullet stripping, sentence segmentation, length/punctuation filters |
| `backend/tests/test_mcq_generator.py` | 3 | Well-formed options, duplicate-free distractors, empty-input handling |
| `backend/tests/test_fib_generator.py` | 2 | Correct blanking, empty-input handling |
| `backend/tests/test_tf_generator.py` | 2 | Boolean answers, empty-input handling |
| `backend/tests/test_semantic_storage.py` | 3 | ChromaDB store/query, related-doc self-exclusion |
| `backend/tests/test_summarizer.py` | 1 | Gemini summarization call |
| `backend/tests/test_chatbot.py` | 2 | RAG retrieval + Gemini answer, with/without history |
| `backend/tests/test_attempts.py` | 4 | Quiz persistence, grading logic, score-history round trip |
| `backend/tests/test_pdf_export.py` | 2 | Valid PDF bytes for both quiz and results export |
| `backend/tests/test_api_routes.py` | 13 | Every REST endpoint, success and error paths |
| `frontend/src/components/__tests__/` | 6 | `QuestionCard`, `OptionButton`, `ProgressBar` |
| `frontend/src/pages/__tests__/` | 6 | Upload submission/validation, quiz answer/submit flow, results rendering |

Run them yourself: `venv\Scripts\python.exe -m pytest` (backend) and `npm run test` (frontend) — see [Running tests](#running-tests).

## Architecture

```
React SPA (Vite)  <-- REST/JSON -->  Flask API
                                        |-- Input Layer: PDF/DOCX/PPTX/TXT/URL extraction
                                        |-- Preprocessing: spaCy clean + segment
                                        |-- Question Generation: instruct LLM + BERT + WordNet (HF Inference API)
                                        |-- Semantic Storage: Sentence-BERT embeddings -> ChromaDB
                                        |-- Chatbot/Summarization: Gemini (RAG via ChromaDB)
                                        `-- SQLite: documents, quizzes, score history
```

Full module-by-module breakdown is in [doc.md](doc.md).

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Flask, Python 3.12 |
| MCQ/FIB/T-F generation | Hugging Face Inference API — `Qwen/Qwen2.5-7B-Instruct`, `google-bert/bert-base-uncased`, `sentence-transformers/all-MiniLM-L6-v2` |
| Summarization + Chatbot | Google Gemini (`gemini-flash-latest`) |
| NLP pipeline | spaCy (`en_core_web_sm`), NLTK WordNet |
| Vector store | ChromaDB (local persistent) |
| Evaluation | `language_tool_python` (grammar), `rouge-score` (ROUGE-L) |
| Persistence | SQLite (documents, quizzes, attempts) |
| PDF export | `xhtml2pdf` (pure Python — see note below) |
| Frontend | React 19 (Vite), Tailwind CSS, React Router 8, Recharts |
| Testing | pytest + pytest-mock (backend, all external APIs mocked), Vitest + Testing Library (frontend) |

**Note on PDF export**: the original plan called for WeasyPrint, but it
requires the native GTK/Pango/Cairo runtime which isn't present on a stock
Windows install (and would need a separate system-wide installer). `xhtml2pdf`
is pure Python and needs nothing beyond `pip install`, so it was used instead
— same HTML-template-in, PDF-out interface.

**Note on models**: the paper specifies FLAN-T5 for MCQ question formation and
Gemini 1.5 Flash for summarization/chat. Both have since been retired from
their respective hosted APIs (Hugging Face's current Inference Providers only
route chat/instruct models for text generation, not plain text2text-generation
models like FLAN-T5; Google retired the 1.5 line). `Qwen/Qwen2.5-7B-Instruct`
and `gemini-flash-latest` (an alias Google keeps pointed at their current
recommended flash model) fill the same roles — configurable via
`QUESTION_GEN_MODEL` and `GEMINI_MODEL` in `.env` if you want to swap them.
Bare Hugging Face model names like `bert-base-uncased` also no longer resolve
through the Inference Providers router; the namespaced form
(`google-bert/bert-base-uncased`) is required.

## Prerequisites

- Python 3.12 (3.13/3.14 currently lack prebuilt wheels for some dependencies,
  notably `chroma-hnswlib`, on Windows)
- Node.js 18+
- A [Hugging Face access token](https://huggingface.co/settings/tokens) (`HF_TOKEN`)
- A [Google Gemini API key](https://aistudio.google.com/apikey) (`GEMINI_API_KEY`)

Without the two API keys, the app still runs: uploading, Fill-in-the-Blank,
True/False, related-documents, and score history all work with **no external
API calls**. Only MCQ generation, summarization, and the chatbot need the
keys — those endpoints return a `502` with an explanatory error if the keys
are missing or the call fails, rather than crashing.

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows (PowerShell: if this errors with a
                                # script-execution message, either run
                                # `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
                                # once, or just call venv\Scripts\python.exe directly)
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader wordnet omw-1.4

copy .env.example .env         # Windows: copy, macOS/Linux: cp
# then edit .env and set HF_TOKEN and GEMINI_API_KEY

python app.py                  # runs on http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install

copy .env.example .env         # optional — defaults to http://localhost:5000

npm run dev                    # runs on http://localhost:5173
```

Open http://localhost:5173.

## Running tests

```bash
# Backend — all Hugging Face / Gemini calls are mocked, no API keys needed
cd backend
venv\Scripts\python.exe -m pytest

# Frontend
cd frontend
npm run test
```

## API reference

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/documents` | Upload a file (`multipart/form-data`, field `file`) or JSON `{url}` / `{text}` |
| GET | `/api/documents` | List uploaded documents |
| GET | `/api/documents/:id/summary` | Gemini summary (cached after first call) |
| GET | `/api/documents/:id/related` | ChromaDB similarity search for related documents |
| POST | `/api/documents/:id/chat` | `{message, history?}` -> `{answer}` |
| POST | `/api/documents/:id/quiz/{mcq\|fib\|tf}` | `{count?, difficulty?}` (difficulty is MCQ-only) -> quiz with questions |
| POST | `/api/quiz/:quizId/submit` | `{answers: {questionId: answer}, session_id?}` -> scored attempt |
| GET | `/api/sessions/:sessionId/attempts` | Score history for that browser session |
| GET | `/api/quiz/:quizId/export.pdf` | Download the quiz as PDF |
| GET | `/api/quiz/:quizId/results/:attemptId/export.pdf` | Download the results as PDF |

## Evaluation metrics

`modules/evaluation/metrics.py` reproduces every metric in the paper's Tables
1–5 (Question Coherence, Distractor Diversity/Similarity, Grammar Check, MCQ
Balance, Keyword Importance, Sentence/Statement Coherence, Answer
Predictability, False Statement Plausibility, ROUGE-L, Coverage, Semantic
Similarity) as **real, computed measures** — cosine similarity over
Sentence-BERT embeddings, `language_tool_python` grammar checking, and
`rouge-score` — not hardcoded constants. Scores will vary by document and
model responses rather than reproducing the paper's exact numbers; that's
expected, since they're computed fresh from whatever you generate.

## Project structure

```
EDUDELL/
  doc.md                 # full design/build plan
  README.md              # this file
  screenshots/             # captured screenshots + sample PDF exports (this test pass)
  sample_files/            # generated sample documents used for testing
  backend/
    app.py, config.py, requirements.txt
    modules/               # extraction, preprocessing, question_generation, semantic,
                            # summarization, chatbot, evaluation, storage, export
    tests/
  frontend/
    src/
      api/, context/, components/, pages/
```

## Future scope

Carried over from the paper's own future work, not implemented in this build:
multilingual support (NLLB/MarianMT), a teacher dashboard with analytics,
speech/OCR input, a mobile app, and gamification (points/badges/timed quizzes).

## License and attribution

The **code** in this repository (`backend/`, `frontend/`) is provided for
educational and research use. The **paper** itself is © Springer Nature / the authors, published under
Springer's standard chapter terms — republishing its full text is subject to
Springer's copyright, independent of whatever license you choose for the
code. If you publish this repository, pick an explicit code license (e.g.
MIT) and keep the citation above intact rather than implying the paper text
itself is open-licensed.
