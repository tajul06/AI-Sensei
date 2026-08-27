import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

interface Props {
  onSend: (text: string) => void
  disabled: boolean
  placeholder?: string
}

export default function MessageInput({ onSend, disabled, placeholder }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-grow textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
  }, [value])

  function handleSend() {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="input-area">
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          id="message-input"
          className="message-textarea"
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder ?? 'Ask a question about your study material…'}
          disabled={disabled}
          rows={1}
          aria-label="Message input"
        />
        <div className="input-footer">
          <span className="input-hint">Enter to send · Shift+Enter for new line</span>
          <button
            id="send-message-btn"
            className="send-btn"
            onClick={handleSend}
            disabled={!value.trim() || disabled}
            aria-label="Send message"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
