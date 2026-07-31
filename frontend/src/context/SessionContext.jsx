import { createContext, useContext, useState } from "react";

const SessionContext = createContext(null);
const STORAGE_KEY = "edudell-session-id";

function getOrCreateSessionId() {
  let sessionId = localStorage.getItem(STORAGE_KEY);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEY, sessionId);
  }
  return sessionId;
}

export function SessionProvider({ children }) {
  const [sessionId] = useState(getOrCreateSessionId);
  return <SessionContext.Provider value={sessionId}>{children}</SessionContext.Provider>;
}

export function useSessionId() {
  const context = useContext(SessionContext);
  if (!context) throw new Error("useSessionId must be used within a SessionProvider");
  return context;
}
