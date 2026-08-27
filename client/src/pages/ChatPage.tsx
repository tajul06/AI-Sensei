import { useState, useEffect, useCallback } from 'react'
import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'
import MessageInput from '../components/MessageInput'
import NewSessionModal from '../components/NewSessionModal'
import UploadModal from '../components/UploadModal'
import ToastContainer from '../components/ToastContainer'
import type { Message } from '../components/ChatWindow'
import type { Toast } from '../components/ToastContainer'
import { listSessions, fetchHistory, askQuestion } from '../lib/api'
import type { ChatSession } from '../lib/api'
import { SUBJECT_ICONS, SUBJECT_COLORS } from '../lib/constants'
import type { Subject } from '../lib/constants'

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loadingSessions, setLoadingSessions] = useState(true)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [asking, setAsking] = useState(false)
  const [showNewSession, setShowNewSession] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [toasts, setToasts] = useState<Toast[]>([])

  // Load sessions on mount
  useEffect(() => {
    loadSessions()
  }, [])

  async function loadSessions() {
    setLoadingSessions(true)
    try {
      const res = await listSessions()
      setSessions(res.sessions)
    } catch {
      addToast('error', 'Failed to load sessions')
    } finally {
      setLoadingSessions(false)
    }
  }

  async function selectSession(session: ChatSession) {
    setActiveSession(session)
    setMessages([])
    setLoadingHistory(true)
    try {
      const res = await fetchHistory(session.id)
      const mapped: Message[] = res.messages.map(m => ({
        id: `${m.created_at ?? Math.random()}-${m.role}`,
        role: m.role as 'user' | 'assistant',
        content: m.content,
      }))
      setMessages(mapped)
    } catch {
      addToast('error', 'Failed to load chat history')
    } finally {
      setLoadingHistory(false)
    }
  }

  async function handleSend(text: string) {
    if (!activeSession) return

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
    }

    // Setup placeholder for AI message
    const aiMsgId = `ai-${Date.now()}`
    const initialAiMsg: Message = {
      id: aiMsgId,
      role: 'assistant',
      content: '', // Will stream into this
      sources: [], // Sources aren't currently returned by the text stream
    }

    setMessages(prev => [...prev, userMsg, initialAiMsg])
    setAsking(true)

    try {
      await askQuestion(text, activeSession.subject, activeSession.id, (chunk) => {
        setMessages(prev =>
          prev.map(m =>
            m.id === aiMsgId
              ? { ...m, content: m.content + chunk }
              : m
          )
        )
      })
    } catch (err: unknown) {
      addToast('error', err instanceof Error ? err.message : 'Failed to get response')
      // Remove the optimistic messages on failure
      setMessages(prev => prev.filter(m => m.id !== userMsg.id && m.id !== aiMsgId))
    } finally {
      setAsking(false)
    }
  }

  function handleSessionCreated(session: ChatSession) {
    setSessions(prev => [session, ...prev])
    selectSession(session)
  }

  const addToast = useCallback((type: Toast['type'], message: string) => {
    const id = `toast-${Date.now()}-${Math.random()}`
    setToasts(prev => [...prev, { id, type, message }])
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const subj = activeSession?.subject as Subject | undefined

  return (
    <div className="app-layout">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSession?.id ?? null}
        onSelectSession={selectSession}
        onNewSession={() => setShowNewSession(true)}
        onUpload={() => setShowUpload(true)}
        loading={loadingSessions}
      />

      <main className="chat-area">
        {!activeSession ? (
          <div className="no-session-screen">
            <div className="no-session-icon">🎓</div>
            <h2>Welcome to AI Sensei</h2>
            <p>Select a session from the sidebar or start a new chat to begin studying.</p>
            <button
              id="welcome-new-chat-btn"
              className="btn-primary"
              style={{ marginTop: 8 }}
              onClick={() => setShowNewSession(true)}
            >
              Start New Chat
            </button>
          </div>
        ) : (
          <>
            {/* Chat header */}
            <div className="chat-header">
              <div className="chat-header-info">
                <div
                  className="chat-subject-badge"
                  style={{
                    color: subj ? SUBJECT_COLORS[subj] : 'var(--accent-primary)',
                    borderColor: subj ? `${SUBJECT_COLORS[subj]}44` : 'var(--border-moderate)',
                    background: subj ? `${SUBJECT_COLORS[subj]}11` : 'transparent',
                  }}
                >
                  <span>{subj ? SUBJECT_ICONS[subj] : '📚'}</span>
                  <span>{activeSession.subject}</span>
                </div>
                {loadingHistory && (
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Loading history…</span>
                )}
              </div>

            </div>

            {/* Messages */}
            <ChatWindow
              messages={messages}
              loading={asking || loadingHistory}
              subject={(activeSession.subject as Subject) ?? 'Physics'}
              onSuggestion={text => handleSend(text)}
            />

            {/* Input */}
            <MessageInput
              onSend={handleSend}
              disabled={asking || loadingHistory}
              placeholder={`Ask about ${activeSession.subject}…`}
            />
          </>
        )}
      </main>

      {/* Modals */}
      {showNewSession && (
        <NewSessionModal
          onClose={() => setShowNewSession(false)}
          onCreated={handleSessionCreated}
          onError={msg => addToast('error', msg)}
        />
      )}

      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onSuccess={msg => addToast('success', msg)}
          onError={msg => addToast('error', msg)}
          defaultSubject={(activeSession?.subject as Subject) ?? undefined}
        />
      )}

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  )
}
