import { Plus, Upload, LogOut, FileUp } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { SUBJECT_COLORS, SUBJECT_ICONS } from '../lib/constants'
import type { Subject } from '../lib/constants'
import type { ChatSession } from '../lib/api'

interface Props {
  sessions: ChatSession[]
  activeSessionId: string | null
  onSelectSession: (session: ChatSession) => void
  onNewSession: () => void
  onUpload: () => void
  loading: boolean
}

function formatDate(iso: string) {
  const d = new Date(iso)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return d.toLocaleDateString([], { weekday: 'short' })
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onUpload,
  loading,
}: Props) {
  const { user, signOut } = useAuth()

  const emailInitial = user?.email?.[0]?.toUpperCase() ?? '?'
  const shortEmail = user?.email ?? ''

  return (
    <aside className="sidebar">
      {/* Brand — no upload button here */}
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">🎓</div>
          <span className="sidebar-brand-name">AI Sensei</span>
        </div>
      </div>

      {/* Action buttons */}
      <div className="sidebar-actions">
        <button id="new-chat-btn" className="new-chat-btn" onClick={onNewSession}>
          <Plus size={16} />
          New Chat
        </button>

        {/* Prominent Upload PDF button */}
        <button id="upload-pdf-btn" className="upload-pdf-btn" onClick={onUpload}>
          <FileUp size={16} />
          Upload PDF
        </button>

        {/* Helper text */}
        <p className="upload-hint">
          📌 Upload your textbook or notes before asking questions
        </p>
      </div>

      {/* Sessions list */}
      <div className="sidebar-sessions">
        {loading ? (
          <>
            {[1, 2, 3].map(i => (
              <div key={i} style={{ padding: '9px 10px', display: 'flex', gap: 10, alignItems: 'center' }}>
                <div className="skeleton" style={{ width: 8, height: 8, borderRadius: '50%' }} />
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <div className="skeleton" style={{ height: 12, width: '60%', borderRadius: 4 }} />
                  <div className="skeleton" style={{ height: 10, width: '35%', borderRadius: 4 }} />
                </div>
              </div>
            ))}
          </>
        ) : sessions.length === 0 ? (
          <div style={{ padding: '20px 12px', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
            No sessions yet.<br />Click <strong>New Chat</strong> to begin.
          </div>
        ) : (
          <>
            <div className="sessions-label">Recent Sessions</div>
            {sessions.map(session => {
              const subj = session.subject as Subject
              const color = SUBJECT_COLORS[subj] ?? '#7c6af7'
              const icon = SUBJECT_ICONS[subj] ?? '📚'
              const isActive = session.id === activeSessionId

              return (
                <div
                  key={session.id}
                  id={`session-${session.id}`}
                  className={`session-item ${isActive ? 'active' : ''}`}
                  onClick={() => onSelectSession(session)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={e => e.key === 'Enter' && onSelectSession(session)}
                  aria-current={isActive ? 'true' : 'false'}
                >
                  <div
                    className="session-subject-dot"
                    style={{ backgroundColor: color }}
                    title={subj}
                  />
                  <div className="session-info">
                    <div className="session-subject-name">{icon} {subj}</div>
                    <div className="session-date">{formatDate(session.created_at)}</div>
                  </div>
                </div>
              )
            })}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="user-avatar">{emailInitial}</div>
        <span className="user-email" title={shortEmail}>{shortEmail}</span>
        <button
          id="signout-btn"
          className="icon-btn"
          onClick={signOut}
          title="Sign out"
          aria-label="Sign out"
        >
          <LogOut size={15} />
        </button>
      </div>
    </aside>
  )
}
