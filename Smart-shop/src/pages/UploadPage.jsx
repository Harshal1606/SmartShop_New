import { VideoUploader } from '../components/upload/VideoUploader.jsx'

export function UploadPage() {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <div className="text-lg font-semibold text-white">Upload CCTV Video</div>
        <div className="mt-1 text-sm text-slate-400">
          Upload footage to generate analytics. Processing is mocked until the backend is ready.
        </div>
      </div>

      <VideoUploader />
    </div>
  )
}

