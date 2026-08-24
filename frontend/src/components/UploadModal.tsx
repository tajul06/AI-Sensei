import { useState, useRef } from 'react'
import { X, Upload, FileText, Trash2 } from 'lucide-react'
import { uploadPdfs } from '../lib/api'
import { SUBJECTS } from '../lib/constants'
import type { Subject } from '../lib/constants'

interface Props {
  onClose: () => void
  onSuccess: (msg: string) => void
  onError: (msg: string) => void
  defaultSubject?: Subject
}

export default function UploadModal({ onClose, onSuccess, onError, defaultSubject }: Props) {
  const [subject, setSubject] = useState<Subject>(defaultSubject ?? 'Physics')
  const [files, setFiles] = useState<File[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  function addFiles(newFiles: FileList | null) {
    if (!newFiles) return
    const pdfs = Array.from(newFiles).filter(f => f.type === 'application/pdf')
    setFiles(prev => [...prev, ...pdfs])
  }

  function removeFile(index: number) {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  function formatSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  async function handleUpload() {
    if (!files.length) return
    setUploading(true)
    setProgress(10)

    // Simulate progress while waiting
    const interval = setInterval(() => {
      setProgress(p => Math.min(p + 8, 85))
    }, 500)

    try {
      const result = await uploadPdfs(files, subject)
      clearInterval(interval)
      setProgress(100)
      setTimeout(() => {
        onSuccess(result.message)
        onClose()
      }, 400)
    } catch (err: unknown) {
      clearInterval(interval)
      setUploading(false)
      setProgress(0)
      onError(err instanceof Error ? err.message : 'Upload failed')
    }
  }

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-card" role="dialog" aria-modal="true" aria-labelledby="upload-modal-title">
        <div className="modal-header">
          <h2 className="modal-title" id="upload-modal-title">Upload Study Material</h2>
          <button id="upload-modal-close" className="icon-btn" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <div className="form-group">
            <label htmlFor="upload-subject-select">Subject</label>
            <select
              id="upload-subject-select"
              className="select-input"
              value={subject}
              onChange={e => setSubject(e.target.value as Subject)}
              disabled={uploading}
            >
              {SUBJECTS.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div
            className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
            onClick={() => inputRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={e => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files) }}
            role="button"
            tabIndex={0}
            id="pdf-drop-zone"
            aria-label="Drop PDFs here or click to browse"
            onKeyDown={e => e.key === 'Enter' && inputRef.current?.click()}
          >
            <div className="drop-zone-icon">📄</div>
            <p>Drop PDF files here or <strong>click to browse</strong></p>
            <span>PDF only · Max 25 MB per file · Max 20 pages</span>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf"
              multiple
              style={{ display: 'none' }}
              onChange={e => addFiles(e.target.files)}
            />
          </div>

          {files.length > 0 && (
            <div className="file-list">
              {files.map((f, i) => (
                <div key={i} className="file-item">
                  <FileText size={14} color="var(--accent-primary)" />
                  <span className="file-item-name">{f.name}</span>
                  <span className="file-item-size">{formatSize(f.size)}</span>
                  {!uploading && (
                    <button
                      id={`remove-file-${i}`}
                      className="icon-btn"
                      onClick={() => removeFile(i)}
                      aria-label={`Remove ${f.name}`}
                    >
                      <Trash2 size={13} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}

          {uploading && (
            <div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }} />
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: 6 }}>
                Processing files… {progress < 90 ? 'Embedding…' : 'Almost done!'}
              </p>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button id="upload-cancel-btn" className="btn-ghost" onClick={onClose} disabled={uploading}>Cancel</button>
          <button
            id="upload-submit-btn"
            className="btn-primary"
            onClick={handleUpload}
            disabled={!files.length || uploading}
          >
            <Upload size={14} style={{ marginRight: 6 }} />
            {uploading ? 'Uploading…' : `Upload ${files.length || ''} File${files.length !== 1 ? 's' : ''}`}
          </button>
        </div>
      </div>
    </div>
  )
}
