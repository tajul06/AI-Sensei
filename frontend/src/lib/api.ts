import { supabase } from './supabase'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function getToken(): Promise<string> {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (!token) throw new Error('Not authenticated')
  return token
}

async function authHeaders(): Promise<HeadersInit> {
  const token = await getToken()
  return { Authorization: `Bearer ${token}` }
}

// ─── Types ────────────────────────────────────────────────────────────────────

export interface SourceDocument {
  page_content: string
  metadata: Record<string, unknown>
}

export interface AskResponse {
  result: string
  source_documents: SourceDocument[]
}

export interface ChatSession {
  id: string
  subject: string
  created_at: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  created_at?: string
}

// ─── Endpoints ────────────────────────────────────────────────────────────────

/** POST /ask/ — ask a question in a session */
export async function askQuestion(
  userQuery: string,
  subject: string,
  sessionId: string
): Promise<AskResponse> {
  const headers = await authHeaders()
  const body = new FormData()
  body.append('user_query', userQuery)
  body.append('subject', subject)
  body.append('session_id', sessionId)

  const res = await fetch(`${BASE_URL}/ask/`, { method: 'POST', headers, body })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.message ?? `Request failed: ${res.status}`)
  }
  return res.json()
}

/** POST /upload_pdf/ — upload one or more PDFs for a subject */
export async function uploadPdfs(files: File[], subject: string): Promise<{ message: string }> {
  const headers = await authHeaders()
  const body = new FormData()
  files.forEach((f) => body.append('files', f))
  body.append('subject', subject)

  const res = await fetch(`${BASE_URL}/upload_pdf/`, { method: 'POST', headers, body })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.message ?? `Upload failed: ${res.status}`)
  }
  return res.json()
}

/** POST /chat_sessions/ — create a new session */
export async function createSession(subject: string): Promise<{ session_id: string }> {
  const headers = await authHeaders()
  const body = new FormData()
  body.append('subject', subject)

  const res = await fetch(`${BASE_URL}/chat_sessions/`, { method: 'POST', headers, body })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.message ?? `Session creation failed: ${res.status}`)
  }
  return res.json()
}

/** GET /chat_sessions/ — list all sessions for the current user */
export async function listSessions(): Promise<{ sessions: ChatSession[] }> {
  const headers = await authHeaders()
  const res = await fetch(`${BASE_URL}/chat_sessions/`, { method: 'GET', headers })
  if (!res.ok) throw new Error(`Failed to list sessions: ${res.status}`)
  return res.json()
}

/** GET /chat_sessions/{session_id}/history — full message history */
export async function fetchHistory(sessionId: string): Promise<{ messages: ChatMessage[] }> {
  const headers = await authHeaders()
  const res = await fetch(`${BASE_URL}/chat_sessions/${sessionId}/history`, {
    method: 'GET',
    headers,
  })
  if (!res.ok) throw new Error(`Failed to fetch history: ${res.status}`)
  return res.json()
}
