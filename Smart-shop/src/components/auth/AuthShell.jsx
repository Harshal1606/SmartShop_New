import { Link } from 'react-router-dom'
import { Logo } from '../branding/Logo.jsx'

export function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="min-h-[calc(100vh-64px)]">
      <div className="container-page flex min-h-[calc(100vh-64px)] items-center justify-center py-10">
        <div className="w-full max-w-md">
          <Link to="/" className="mb-6 inline-flex">
            <Logo />
          </Link>
          <div className="card p-6 sm:p-7">
            <div className="text-xl font-semibold text-white">{title}</div>
            {subtitle ? <div className="mt-1 text-sm text-slate-400">{subtitle}</div> : null}
            <div className="mt-6">{children}</div>
          </div>
          {footer ? <div className="mt-4 text-sm text-slate-400">{footer}</div> : null}
        </div>
      </div>
    </div>
  )
}

