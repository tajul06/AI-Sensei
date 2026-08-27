import { useState } from 'react'
import { X } from 'lucide-react'
import { createSession } from '../lib/api'
import { SUBJECTS, SUBJECT_ICONS, SUBJECT_COLORS } from '../lib/constants'
import type { Subject } from '../lib/constants'
import type { ChatSession } from '../lib/api'

interface Props {
  onClose: () => void
  onCreated: (session: ChatSession) => void
  onError: (msg: string) => void
}

export default function NewSessionModal({ onClose, onCreated, onError }: Props) {
  const [subject, setSubject] = useState<Subject>('Physics')
  const [loading, setLoading] = useState(false)

  async function handleCreate() {
    setLoading(true)
    try {
      const res = await createSession(subject)
      const now = new Date().toISOString()
      const newSession: ChatSession = { id: res.session_id, subject, created_at: now }
      onCreated(newSession)
      onClose()
    } catch (err: unknown) {
      onError(err instanceof Error ? err.message : 'Failed to create session')
      setLoading(false)
    }
  }

  const color = SUBJECT_COLORS[subject]

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-card" role="dialog" aria-modal="true" aria-labelledby="new-session-title">
        <div className="modal-header">
          <h2 className="modal-title" id="new-session-title">New Chat Session</h2>
          <button id="new-session-close" className="icon-btn" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <div className="form-group">
            <label htmlFor="session-subject-select">Choose a Subject</label>
            <select
              id="session-subject-select"
              className="select-input"
              value={subject}
              onChange={e => setSubject(e.target.value as Subject)}
            >
              {SUBJECTS.map(s => (
                <option key={s} value={s}>{SUBJECT_ICONS[s]} {s}</option>
              ))}
            </select>
          </div>

          {/* Subject preview card */}
          <div style={{
            padding: '16px',
            background: 'var(--bg-elevated)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            gap: '14px',
          }}>
            <div style={{
              width: 48,
              height: 48,
              borderRadius: 'var(--radius-sm)',
              background: `${color}22`,
              border: `1px solid ${color}44`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
            }}>
              {SUBJECT_ICONS[subject]}
            </div>
            <div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 15 }}>{subject}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                A new chat session will be created
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button id="new-session-cancel" className="btn-ghost" onClick={onClose} disabled={loading}>Cancel</button>
          <button
            id="new-session-create-btn"
            className="btn-primary"
            onClick={handleCreate}
            disabled={loading}
          >
            {loading ? 'Creating…' : 'Start Chat'}
          </button>
        </div>
      </div>
    </div>
  )
}
