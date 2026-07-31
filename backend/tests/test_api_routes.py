import json

from tests.conftest import SAMPLE_TEXT


def _upload_sample_document(client):
    response = client.post("/api/documents", json={"text": SAMPLE_TEXT})
    assert response.status_code == 201
    return response.get_json()


def test_upload_document_via_raw_text(client):
    body = _upload_sample_document(client)
    assert body["sentence_count"] > 0
    assert body["filename"] == "Pasted text"


def test_upload_document_requires_input(client):
    response = client.post("/api/documents", json={})
    assert response.status_code == 400


def test_list_documents_includes_uploaded_document(client):
    body = _upload_sample_document(client)
    response = client.get("/api/documents")
    ids = [d["id"] for d in response.get_json()]
    assert body["id"] in ids


def test_document_summary_returns_mocked_gemini_text(client):
    document = _upload_sample_document(client)
    response = client.get(f"/api/documents/{document['id']}/summary")
    assert response.status_code == 200
    assert "mocked Gemini response" in response.get_json()["summary"]


def test_document_summary_missing_document_returns_404(client):
    response = client.get("/api/documents/does-not-exist/summary")
    assert response.status_code == 404


def test_document_related_returns_list(client):
    document = _upload_sample_document(client)
    response = client.get(f"/api/documents/{document['id']}/related")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_document_chat_returns_answer(client):
    document = _upload_sample_document(client)
    response = client.post(f"/api/documents/{document['id']}/chat", json={"message": "What is this about?"})
    assert response.status_code == 200
    assert "answer" in response.get_json()


def test_document_chat_requires_message(client):
    document = _upload_sample_document(client)
    response = client.post(f"/api/documents/{document['id']}/chat", json={"message": ""})
    assert response.status_code == 400


def test_generate_mcq_quiz(client):
    document = _upload_sample_document(client)
    response = client.post(
        f"/api/documents/{document['id']}/quiz/mcq", json={"count": 3, "difficulty": "medium"}
    )
    assert response.status_code == 201
    quiz = response.get_json()
    assert quiz["quiz_type"] == "mcq"
    assert len(quiz["questions"]) >= 1


def test_generate_quiz_unknown_type_returns_400(client):
    document = _upload_sample_document(client)
    response = client.post(f"/api/documents/{document['id']}/quiz/essay", json={})
    assert response.status_code == 400


def test_submit_quiz_and_fetch_history(client):
    document = _upload_sample_document(client)
    quiz = client.post(f"/api/documents/{document['id']}/quiz/fib", json={"count": 2}).get_json()

    answers = {str(q["id"]): q["correct_answer"] for q in quiz["questions"]}
    submit_response = client.post(
        f"/api/quiz/{quiz['id']}/submit", json={"answers": answers, "session_id": "session-xyz"}
    )
    assert submit_response.status_code == 201
    attempt = submit_response.get_json()
    assert attempt["score"] == attempt["total"]

    history_response = client.get("/api/sessions/session-xyz/attempts")
    assert history_response.status_code == 200
    assert len(history_response.get_json()) == 1


def test_download_quiz_pdf(client):
    document = _upload_sample_document(client)
    quiz = client.post(f"/api/documents/{document['id']}/quiz/tf", json={"count": 2}).get_json()

    response = client.get(f"/api/quiz/{quiz['id']}/export.pdf")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")


def test_download_results_pdf(client):
    document = _upload_sample_document(client)
    quiz = client.post(f"/api/documents/{document['id']}/quiz/mcq", json={"count": 2}).get_json()
    answers = {str(q["id"]): q["correct_answer"] for q in quiz["questions"]}
    attempt = client.post(f"/api/quiz/{quiz['id']}/submit", json={"answers": answers}).get_json()

    response = client.get(f"/api/quiz/{quiz['id']}/results/{attempt['id']}/export.pdf")
    assert response.status_code == 200
    assert response.data.startswith(b"%PDF")
