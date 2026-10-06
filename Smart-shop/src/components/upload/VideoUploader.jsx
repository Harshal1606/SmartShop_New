import { useEffect, useMemo, useRef, useState } from 'react'
import { Button } from '../ui/Button.jsx'
import { uploadVideoMock } from '../../services/uploadService.js'

const ACCEPTED_EXT = ['mp4', 'mov', 'avi']
const ACCEPTED_MIME = ['video/mp4', 'video/quicktime', 'video/x-msvideo']

function getExt(name = '') {
  const parts = String(name).split('.')
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : ''
}

function isAcceptedFile(file) {
  if (!file) return false
  const ext = getExt(file.name)
  if (ACCEPTED_EXT.includes(ext)) return true
  if (file.type && ACCEPTED_MIME.includes(file.type)) return true
  return false
}

export function VideoUploader() {
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('idle') // idle | uploading | success | error
  const [error, setError] = useState('')

  useEffect(() => {
    if (!file) return
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  const acceptHint = useMemo(() => ACCEPTED_EXT.map((x) => `.${x}`).join(', '), [])

  const onPick = (picked) => {
    setError('')
    setStatus('idle')
    setProgress(0)

    if (!picked) return
    if (!isAcceptedFile(picked)) {
      setFile(null)
      setPreviewUrl('')
      setError('Invalid file type. Please upload an mp4, mov, or avi video.')
      return
    }
    setFile(picked)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files?.[0]
    onPick(dropped)
  }

  const onUpload = async () => {
    if (!file) {
      setError('Please select a video file first.')
      return
    }
    setError('')
    setStatus('uploading')
    setProgress(0)

    try {
      // Mock upload today; swap to uploadVideoApi(...) when backend is ready.
      await uploadVideoMock(file, {
        onProgress: (p) => setProgress(p),
      })
      setStatus('success')
    } catch (e) {
      setStatus('error')
      setError(e?.message || 'Upload failed. Please try again.')
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <div className="lg:col-span-3">
        <div
          className={[
            'card p-6',
            isDragging ? 'ring-2 ring-indigo-400/40' : '',
          ].join(' ')}
          onDragEnter={(e) => {
            e.preventDefault()
            setIsDragging(true)
          }}
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragging(true)
          }}
          onDragLeave={(e) => {
            e.preventDefault()
            setIsDragging(false)
          }}
          onDrop={onDrop}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
          }}
          onClick={() => inputRef.current?.click()}
        >
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-white/15 bg-white/5 p-10 text-center">
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-indigo-500/15 ring-1 ring-indigo-400/30">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 3v10m0-10 4 4m-4-4L8 7"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M4 14v4a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3v-4"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              </svg>
            </div>

            <div className="mt-4 text-base font-semibold text-white">
              Drag & drop a video to upload
            </div>
            <div className="mt-1 text-sm text-slate-400">
              or click to choose a file ({acceptHint})
            </div>

            <input
              ref={inputRef}
              type="file"
              accept={acceptHint}
              className="hidden"
              onChange={(e) => onPick(e.target.files?.[0] || null)}
            />
          </div>

          {error ? <div className="mt-3 text-sm text-rose-300">{error}</div> : null}

          <div className="mt-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-slate-400">
              Endpoint ready: <span className="text-slate-200">POST /api/upload</span>
            </div>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={(e) => {
                  e.stopPropagation()
                  setFile(null)
                  setPreviewUrl('')
                  setProgress(0)
                  setStatus('idle')
                  setError('')
                }}
                disabled={!file || status === 'uploading'}
              >
                Clear
              </Button>
              <Button
                onClick={(e) => {
                  e.stopPropagation()
                  onUpload()
                }}
                isLoading={status === 'uploading'}
              >
                Upload
              </Button>
            </div>
          </div>

          {status !== 'idle' ? (
            <div className="mt-4">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Upload progress</span>
                <span>{progress}%</span>
              </div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-indigo-500 transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              {status === 'success' ? (
                <div className="mt-3 text-sm text-emerald-300">
                  Upload successful. Analytics will appear once processing is available.
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>

      <div className="lg:col-span-2">
        <div className="card p-6">
          <div className="text-sm font-semibold text-white">Preview</div>
          <div className="mt-1 text-xs text-slate-400">
            Selected file will show here before upload.
          </div>

          <div className="mt-4 overflow-hidden rounded-xl border border-white/10 bg-black/20">
            {previewUrl ? (
              <video
                src={previewUrl}
                controls
                className="aspect-video w-full"
                preload="metadata"
              />
            ) : (
              <div className="grid aspect-video place-items-center">
                <div className="text-sm text-slate-500">No file selected</div>
              </div>
            )}
          </div>

          {file ? (
            <div className="mt-4 text-sm">
              <div className="text-slate-200">{file.name}</div>
              <div className="mt-1 text-xs text-slate-400">
                Size: {(file.size / (1024 * 1024)).toFixed(2)} MB
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}

