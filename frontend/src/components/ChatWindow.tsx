import { useRef, useEffect } from 'react'
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ChevronDown, ChevronRight, BookOpen } from 'lucide-react'
import { SUBJECT_ICONS } from '../lib/constants'
import type { Subject } from '../lib/constants'
import type { SourceDocument } from '../lib/api'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: SourceDocument[]
}

interface Props {
  messages: Message[]
  loading: boolean
  subject: Subject
  onSuggestion?: (text: string) => void
}

const SUGGESTIONS: Record<string, string[]> = {
  Physics: ['What is Newton\'s second law?', 'Explain quantum entanglement', 'What is relativity?'],
  Chemistry: ['What is a covalent bond?', 'Explain the periodic table', 'What is pH?'],
  Biology: ['What is DNA?', 'Explain photosynthesis', 'What is cellular respiration?'],
  Math: ['Solve for x: 2x+5=13', 'What is the Pythagorean theorem?', 'Explain derivatives'],
  default: ['Ask me anything about this subject!', 'Summarize my uploaded notes', 'Give me practice questions'],
}

function SourcesAccordion({ sources }: { sources: SourceDocument[] }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="sources-accordion">
      <button
        className="sources-toggle"
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
      >
        {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        <BookOpen size={12} />
        {sources.length} source document{sources.length !== 1 ? 's' : ''}
      </button>
      {open && (
        <div className="sources-body">
          {sources.map((src, i) => {
            const page = src.metadata?.page as number | undefined
            const source = src.metadata?.source as string | undefined
            return (
              <div key={i} className="source-card">
                <div className="source-meta">
                  {source && <span>📄 {String(source).split(/[\\/]/).pop()}</span>}
                  {page !== undefined && <span>Page {page + 1}</span>}
                </div>
                <p className="source-text">{src.page_content}</p>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="message-row ai">
      <div className="message-avatar ai-avatar">🎓</div>
      <div className="message-body">
        <div className="message-bubble">
          <div className="typing-indicator">
            <div className="typing-dot" />
            <div className="typing-dot" />
            <div className="typing-dot" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ChatWindow({ messages, loading, subject, onSuggestion }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  if (messages.length === 0 && !loading) {
    const suggestions = SUGGESTIONS[subject] ?? SUGGESTIONS.default
    return (
      <div className="chat-window">
        <div className="empty-chat">
          <div className="empty-chat-subject-icon">{SUBJECT_ICONS[subject] ?? '📚'}</div>
          <h3>Ask anything about {subject}</h3>
          <p>Upload your PDFs and start asking questions. I'll answer based on your study material.</p>
          {onSuggestion && (
            <div className="suggestions">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  id={`suggestion-${i}`}
                  className="suggestion-chip"
                  onClick={() => onSuggestion(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
        <div ref={bottomRef} />
      </div>
    )
  }

  return (
    <div className="chat-window" id="chat-window-scroll">
      {messages.map(msg => (
        <div
          key={msg.id}
          className={`message-row ${msg.role === 'user' ? 'user' : 'ai'}`}
          id={`msg-${msg.id}`}
        >
          <div className={`message-avatar ${msg.role === 'user' ? 'user-avatar-msg' : 'ai-avatar'}`}>
            {msg.role === 'user' ? '👤' : '🎓'}
          </div>
          <div className="message-body">
            <div className="message-bubble">
              {msg.role === 'assistant' ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              ) : (
                msg.content
              )}
            </div>
            {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
              <SourcesAccordion sources={msg.sources} />
            )}
          </div>
        </div>
      ))}
      {loading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}
