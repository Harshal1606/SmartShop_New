import { api } from './api.js'

/**
 * Upload video (mock for now)
 * Future backend endpoint: POST /api/upload
 */
export async function uploadVideoMock(file, { onProgress } = {}) {
  // Simulate progress + latency
  let progress = 0
  const startedAt = Date.now()

  await new Promise((resolve) => {
    const timer = setInterval(() => {
      const elapsed = Date.now() - startedAt
      const next = Math.min(95, Math.floor(elapsed / 25))
      progress = Math.max(progress, next)
      onProgress?.(progress)
      if (progress >= 95) {
        clearInterval(timer)
        resolve()
      }
    }, 120)
  })

  // Simulate server processing time
  await new Promise((r) => setTimeout(r, 600))
  onProgress?.(100)

  return {
    ok: true,
    fileName: file?.name,
    message: 'Upload complete (mock). Backend integration pending.',
  }
}

export async function uploadVideoApi(file, { onProgress } = {}) {
  const formData = new FormData()
  formData.append('file', file)

  // Note: This is ready for the real backend.
  const res = await api.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (evt) => {
      if (!evt.total) return
      const pct = Math.round((evt.loaded / evt.total) * 100)
      onProgress?.(pct)
    },
  })

  return res.data
}

