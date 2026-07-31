const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: options.body instanceof FormData
      ? options.headers
      : { "Content-Type": "application/json", ...options.headers },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.error || message;
    } catch {
      // response wasn't JSON (e.g. PDF error page) — keep the default message
    }
    throw new ApiError(message, response.status);
  }

  return response;
}

async function requestJson(path, options) {
  const response = await request(path, options);
  return response.json();
}

export const api = {
  uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);
    return requestJson("/api/documents", { method: "POST", body: formData });
  },

  uploadUrl(url) {
    return requestJson("/api/documents", { method: "POST", body: JSON.stringify({ url }) });
  },

  uploadText(text) {
    return requestJson("/api/documents", { method: "POST", body: JSON.stringify({ text }) });
  },

  listDocuments() {
    return requestJson("/api/documents");
  },

  getSummary(documentId) {
    return requestJson(`/api/documents/${documentId}/summary`);
  },

  getRelatedDocuments(documentId) {
    return requestJson(`/api/documents/${documentId}/related`);
  },

  sendChatMessage(documentId, message, history) {
    return requestJson(`/api/documents/${documentId}/chat`, {
      method: "POST",
      body: JSON.stringify({ message, history }),
    });
  },

  generateQuiz(documentId, quizType, { count = 5, difficulty } = {}) {
    return requestJson(`/api/documents/${documentId}/quiz/${quizType}`, {
      method: "POST",
      body: JSON.stringify({ count, difficulty }),
    });
  },

  submitQuiz(quizId, answers, sessionId) {
    return requestJson(`/api/quiz/${quizId}/submit`, {
      method: "POST",
      body: JSON.stringify({ answers, session_id: sessionId }),
    });
  },

  getSessionAttempts(sessionId) {
    return requestJson(`/api/sessions/${sessionId}/attempts`);
  },

  quizPdfUrl(quizId) {
    return `${API_BASE_URL}/api/quiz/${quizId}/export.pdf`;
  },

  resultsPdfUrl(quizId, attemptId) {
    return `${API_BASE_URL}/api/quiz/${quizId}/results/${attemptId}/export.pdf`;
  },
};

export { ApiError };
