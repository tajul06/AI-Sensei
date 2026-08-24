import { useEffect, useRef } from 'react'

export interface Toast {
  id: string
  type: 'success' | 'error'
  message: string
}

interface Props {
  toasts: Toast[]
  onRemove: (id: string) => void
}

export default function ToastContainer({ toasts, onRemove }: Props) {
  return (
    <div className="toast-container" aria-live="polite">
      {toasts.map(t => (
        <ToastItem key={t.id} toast={t} onRemove={onRemove} />
      ))}
    </div>
  )
}

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: string) => void }) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    timerRef.current = setTimeout(() => onRemove(toast.id), 4000)
    return () => { if (timerRef.current) clearTimeout(timerRef.current) }
  }, [toast.id, onRemove])

  const icon = toast.type === 'success' ? '✓' : '✕'

  return (
    <div
      className={`toast ${toast.type}`}
      role="status"
      id={`toast-${toast.id}`}
      onClick={() => onRemove(toast.id)}
      style={{ cursor: 'pointer' }}
    >
      <span>{icon}</span>
      {toast.message}
    </div>
  )
}
