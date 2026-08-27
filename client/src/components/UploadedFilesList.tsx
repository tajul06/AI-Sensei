import { useEffect, useState } from 'react'
import { FileText } from 'lucide-react'
import { listUploadedFiles } from '../lib/api'
import type { UploadedFile } from '../lib/api'
import type { Subject } from '../lib/constants'

interface Props {
  subject: Subject
}

export default function UploadedFilesList({ subject }: Props) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    listUploadedFiles(subject)
      .then(res => setFiles(res.files))
      .catch(() => setFiles([]))
      .finally(() => setLoading(false))
  }, [subject])

  if (loading) {
    return (
      <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '4px 0 8px' }}>
        Loading existing files…
      </p>
    )
  }

  if (files.length === 0) return null

  return (
    <div style={{ marginBottom: 12 }}>
      <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>
        Already uploaded for <strong>{subject}</strong>:
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {files.map(f => (
          <div
            key={f.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '6px 10px',
              background: 'var(--bg-elevated)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <FileText size={13} color="var(--text-muted)" />
            <span style={{ fontSize: 12, color: 'var(--text-secondary)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {f.filename}
            </span>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', flexShrink: 0 }}>
              {new Date(f.uploaded_at).toLocaleDateString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}