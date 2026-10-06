import { Spinner } from './Spinner.jsx'

export function FullPageLoader({ label = 'Loading...' }) {
  return (
    <div className="min-h-screen w-full">
      <div className="container-page flex min-h-screen items-center justify-center">
        <div className="card w-full max-w-md p-6">
          <div className="flex items-center gap-3">
            <Spinner />
            <div className="text-sm text-slate-200">{label}</div>
          </div>
          <div className="mt-3 text-xs text-slate-400">
            Please wait a moment — the backend integration will be wired in later.
          </div>
        </div>
      </div>
    </div>
  )
}

