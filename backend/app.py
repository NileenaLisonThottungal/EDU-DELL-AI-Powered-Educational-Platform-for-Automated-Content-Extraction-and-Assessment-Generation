import uuid

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from config import Config
from modules.chatbot import answer_question
from modules.export.pdf_export import export_quiz_pdf, export_results_pdf
from modules.extraction import (
    UnsafeURLError,
    UnsupportedFileTypeError,
    extract_from_file,
    extract_from_raw_text,
    extract_from_url,
)
from modules.preprocessing import preprocess
from modules.question_generation import generate_fib_questions, generate_mcqs, generate_tf_questions
from modules.quiz_grading import grade_quiz
from modules.semantic import find_related_documents
from modules.semantic import store_document as index_document
from modules.storage import (
    get_attempt,
    get_document,
    get_quiz,
    init_db,
    list_attempts_for_session,
    list_documents,
    save_attempt,
    save_document,
    save_quiz,
    save_summary,
)
from modules.summarization import summarize_document

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_UPLOAD_MB * 1024 * 1024

init_db()

_QUIZ_GENERATORS = {
    "mcq": lambda sentences, count, difficulty: generate_mcqs(sentences, count, difficulty),
    "fib": lambda sentences, count, difficulty: generate_fib_questions(sentences, count),
    "tf": lambda sentences, count, difficulty: generate_tf_questions(sentences, count),
}


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@app.errorhandler(404)
def not_found(_error_obj):
    return _error("Not found.", 404)


@app.post("/api/documents")
def upload_document():
    filename = None
    raw_text = None

    if "file" in request.files:
        uploaded = request.files["file"]
        filename = uploaded.filename or "upload"
        try:
            raw_text = extract_from_file(filename, uploaded.read())
        except UnsupportedFileTypeError as exc:
            return _error(str(exc))
    elif request.is_json:
        body = request.get_json(silent=True) or {}
        if body.get("url"):
            filename = body["url"]
            try:
                raw_text = extract_from_url(body["url"])
            except UnsafeURLError as exc:
                return _error(str(exc))
            except Exception:
                return _error("Could not fetch or parse that URL.", 422)
        elif body.get("text"):
            filename = "Pasted text"
            raw_text = extract_from_raw_text(body["text"])

    if raw_text is None:
        return _error("Provide a 'file', a JSON 'url', or a JSON 'text' field.")

    sentences = preprocess(raw_text)
    if not sentences:
        return _error("No usable text could be extracted from that input.", 422)

    document = save_document(filename, raw_text, sentences)

    try:
        index_document(document["id"], filename, sentences)
    except Exception:
        pass  # semantic indexing is best-effort; chat/related-docs degrade gracefully

    return jsonify(
        {
            "id": document["id"],
            "filename": document["filename"],
            "sentence_count": len(sentences),
            "created_at": document["created_at"],
        }
    ), 201


@app.get("/api/documents")
def documents_list():
    return jsonify(list_documents())


@app.get("/api/documents/<document_id>/summary")
def document_summary(document_id):
    document = get_document(document_id)
    if document is None:
        return _error("Document not found.", 404)

    if document["summary"]:
        return jsonify({"summary": document["summary"]})

    try:
        summary = summarize_document(document["raw_text"])
    except Exception:
        return _error("Summarization service is unavailable.", 502)

    save_summary(document_id, summary)
    return jsonify({"summary": summary})


@app.get("/api/documents/<document_id>/related")
def document_related(document_id):
    if get_document(document_id) is None:
        return _error("Document not found.", 404)

    try:
        related = find_related_documents(document_id)
    except Exception:
        related = []

    return jsonify(related)


@app.post("/api/documents/<document_id>/chat")
def document_chat(document_id):
    document = get_document(document_id)
    if document is None:
        return _error("Document not found.", 404)

    body = request.get_json(silent=True) or {}
    question = (body.get("message") or "").strip()
    if not question:
        return _error("A non-empty 'message' is required.")

    try:
        answer = answer_question(document_id, question, body.get("history"))
    except Exception:
        return _error("Chat service is unavailable.", 502)

    return jsonify({"answer": answer})


@app.post("/api/documents/<document_id>/quiz/<quiz_type>")
def generate_quiz(document_id, quiz_type):
    generator = _QUIZ_GENERATORS.get(quiz_type)
    if generator is None:
        return _error(f"Unknown quiz type '{quiz_type}'. Use mcq, fib, or tf.")

    document = get_document(document_id)
    if document is None:
        return _error("Document not found.", 404)

    body = request.get_json(silent=True) or {}
    count = int(body.get("count", 5))
    difficulty = body.get("difficulty", "medium") if quiz_type == "mcq" else None

    questions = generator(document["sentences"], count, difficulty)
    if not questions:
        return _error("Could not generate questions from this document.", 422)

    quiz = save_quiz(document_id, quiz_type, questions, difficulty)
    return jsonify(quiz), 201


@app.post("/api/quiz/<quiz_id>/submit")
def submit_quiz(quiz_id):
    quiz = get_quiz(quiz_id)
    if quiz is None:
        return _error("Quiz not found.", 404)

    body = request.get_json(silent=True) or {}
    answers = body.get("answers", {})
    session_id = body.get("session_id") or str(uuid.uuid4())

    score, total, breakdown = grade_quiz(quiz, answers)
    attempt = save_attempt(quiz_id, session_id, quiz["quiz_type"], score, total, breakdown)

    return jsonify(attempt), 201


@app.get("/api/sessions/<session_id>/attempts")
def session_attempts(session_id):
    return jsonify(list_attempts_for_session(session_id))


@app.get("/api/quiz/<quiz_id>/export.pdf")
def download_quiz_pdf(quiz_id):
    quiz = get_quiz(quiz_id)
    if quiz is None:
        return _error("Quiz not found.", 404)

    pdf_bytes = export_quiz_pdf(quiz)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=quiz-{quiz_id}.pdf"},
    )


@app.get("/api/quiz/<quiz_id>/results/<attempt_id>/export.pdf")
def download_results_pdf(quiz_id, attempt_id):
    quiz = get_quiz(quiz_id)
    attempt = get_attempt(attempt_id)
    if quiz is None or attempt is None or attempt["quiz_id"] != quiz_id:
        return _error("Quiz or attempt not found.", 404)

    pdf_bytes = export_results_pdf(quiz, attempt)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=results-{attempt_id}.pdf"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
