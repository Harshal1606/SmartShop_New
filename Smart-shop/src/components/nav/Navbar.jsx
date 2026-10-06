import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'
import { Logo } from '../branding/Logo.jsx'
import { Button } from '../ui/Button.jsx'

const linkClass =
  'text-sm text-slate-300 hover:text-white transition px-3 py-2 rounded-lg hover:bg-white/5'

export function Navbar() {
  const { isAuthenticated, logout } = useAuth()
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-slate-950/70 backdrop-blur">
      <div className="container-page">
        <div className="flex h-16 items-center justify-between">
          <Link to="/" className="shrink-0">
            <Logo />
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            <a href="#features" className={linkClass}>
              Features
            </a>
            <a href="#about" className={linkClass}>
              About
            </a>
          </nav>

          <div className="hidden items-center gap-2 md:flex">
            {isAuthenticated ? (
              <>
                <NavLink to="/dashboard">
                  <Button variant="secondary" size="sm">
                    Dashboard
                  </Button>
                </NavLink>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    logout()
                  }}
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
                <NavLink to="/login">
                  <Button variant="ghost" size="sm">
                    Login
                  </Button>
                </NavLink>
                <NavLink to="/signup">
                  <Button variant="primary" size="sm">
                    Get Started
                  </Button>
                </NavLink>
              </>
            )}
          </div>

          <button
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-100 hover:bg-white/10 md:hidden"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path
                d="M4 7h16M4 12h16M4 17h16"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          </button>
        </div>

        {open ? (
          <div className="md:hidden">
            <div className="pb-4 pt-2">
              <div className="flex flex-col gap-1">
                <a href="#features" className={linkClass} onClick={() => setOpen(false)}>
                  Features
                </a>
                <a href="#about" className={linkClass} onClick={() => setOpen(false)}>
                  About
                </a>
              </div>

              <div className="mt-3 flex flex-col gap-2">
                {isAuthenticated ? (
                  <>
                    <NavLink to="/dashboard" onClick={() => setOpen(false)}>
                      <Button variant="secondary" className="w-full">
                        Dashboard
                      </Button>
                    </NavLink>
                    <Button
                      variant="ghost"
                      className="w-full"
                      onClick={() => {
                        logout()
                        setOpen(false)
                      }}
                    >
                      Logout
                    </Button>
                  </>
                ) : (
                  <>
                    <NavLink to="/login" onClick={() => setOpen(false)}>
                      <Button variant="ghost" className="w-full">
                        Login
                      </Button>
                    </NavLink>
                    <NavLink to="/signup" onClick={() => setOpen(false)}>
                      <Button variant="primary" className="w-full">
                        Get Started
                      </Button>
                    </NavLink>
                  </>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </header>
  )
}

