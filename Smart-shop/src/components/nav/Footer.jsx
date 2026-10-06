import { Link } from 'react-router-dom'
import { Logo } from '../branding/Logo.jsx'

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-slate-950">
      <div className="container-page py-10">
        <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
          <div>
            <Link to="/" className="inline-block">
              <Logo />
            </Link>
            <p className="mt-3 max-w-md text-sm text-slate-400">
              AI-powered CCTV insights for retail intelligence. This frontend is API-ready and
              currently runs on mock data while the backend is under development.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-8 text-sm md:grid-cols-3">
            <div>
              <div className="font-medium text-slate-200">Product</div>
              <ul className="mt-3 space-y-2 text-slate-400">
                <li>
                  <a href="#features" className="hover:text-white">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#about" className="hover:text-white">
                    About
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <div className="font-medium text-slate-200">Account</div>
              <ul className="mt-3 space-y-2 text-slate-400">
                <li>
                  <Link to="/login" className="hover:text-white">
                    Login
                  </Link>
                </li>
                <li>
                  <Link to="/signup" className="hover:text-white">
                    Sign up
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <div className="font-medium text-slate-200">Legal</div>
              <ul className="mt-3 space-y-2 text-slate-400">
                <li>Privacy</li>
                <li>Terms</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-col gap-2 border-t border-white/10 pt-6 text-xs text-slate-500 md:flex-row md:items-center md:justify-between">
          <div>© {new Date().getFullYear()} Smart Shop Analytics</div>
          <div>Frontend demo (mock data) • Backend integration pending</div>
        </div>
      </div>
    </footer>
  )
}

