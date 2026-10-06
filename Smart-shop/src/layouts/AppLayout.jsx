import { useMemo, useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { Button } from '../components/ui/Button.jsx'

function getInitials(email) {
  const base = String(email || 'U').split('@')[0] || 'U'
  return base.slice(0, 2).toUpperCase()
}

function SidebarLink({ to, icon, label, collapsed, onNavigate }) {
  return (
    <NavLink
      to={to}
      onClick={onNavigate}
      className={({ isActive }) =>
        [
          'group flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition',
          isActive ? 'bg-white/10 text-white' : 'text-slate-300 hover:bg-white/5 hover:text-white',
        ].join(' ')
      }
    >
      <span className="grid h-9 w-9 place-items-center rounded-xl bg-white/5 ring-1 ring-white/10 group-hover:bg-white/10">
        {icon}
      </span>
      {!collapsed ? <span className="truncate">{label}</span> : null}
    </NavLink>
  )
}

export function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  const navItems = useMemo(
    () => [
      {
        to: '/dashboard',
        label: 'Dashboard',
        icon: (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              d="M4 13h7V4H4v9Zm9 7h7V11h-7v9ZM4 20h7v-5H4v5Zm9-11h7V4h-7v5Z"
              fill="currentColor"
              opacity="0.9"
            />
          </svg>
        ),
      },
      {
        to: '/upload',
        label: 'Upload Video',
        icon: (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
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
        ),
      },
      {
        to: '/reports',
        label: 'Reports',
        icon: (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              d="M6 20V4h9l3 3v13H6Z"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinejoin="round"
            />
            <path
              d="M9 12h6M9 16h6M9 8h3"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
            />
          </svg>
        ),
      },
      {
        to: '/settings',
        label: 'Settings',
        icon: (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"
              stroke="currentColor"
              strokeWidth="1.6"
            />
            <path
              d="M19.4 15a7.97 7.97 0 0 0 .1-1 7.97 7.97 0 0 0-.1-1l2-1.5-2-3.4-2.4 1a8.4 8.4 0 0 0-1.7-1l-.4-2.6H9.5L9.1 8.1a8.4 8.4 0 0 0-1.7 1l-2.4-1-2 3.4 2 1.5a7.97 7.97 0 0 0-.1 1c0 .34.03.67.1 1l-2 1.5 2 3.4 2.4-1c.53.4 1.1.73 1.7 1l.4 2.6h5.1l.4-2.6c.6-.26 1.17-.6 1.7-1l2.4 1 2-3.4-2-1.5Z"
              stroke="currentColor"
              strokeWidth="1.2"
              strokeLinejoin="round"
              opacity="0.9"
            />
          </svg>
        ),
      },
    ],
    [],
  )

  const onLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const pageTitle = useMemo(() => {
    if (location.pathname.startsWith('/upload')) return 'Upload Video'
    if (location.pathname.startsWith('/reports')) return 'Reports'
    if (location.pathname.startsWith('/settings')) return 'Settings'
    return 'Dashboard'
  }, [location.pathname])

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Mobile backdrop */}
      {mobileOpen ? (
        <button
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-label="Close sidebar"
        />
      ) : null}

      {/* Sidebar */}
      <aside
        className={[
          'fixed z-50 h-full border-r border-white/10 bg-slate-950/80 backdrop-blur',
          'transition-all',
          collapsed ? 'w-20' : 'w-72',
          mobileOpen ? 'left-0' : '-left-[400px] lg:left-0',
        ].join(' ')}
      >
        <div className="flex h-16 items-center justify-between px-3">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-500/15 ring-1 ring-indigo-400/30">
              <span className="text-sm font-semibold text-indigo-100">
                {getInitials(user?.email)}
              </span>
            </div>
            {!collapsed ? (
              <div className="leading-tight">
                <div className="text-sm font-semibold text-white">Smart Shop</div>
                <div className="text-xs text-slate-400">Analytics</div>
              </div>
            ) : null}
          </div>
          <button
            className="hidden h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-200 hover:bg-white/10 lg:inline-flex"
            onClick={() => setCollapsed((v) => !v)}
            aria-label="Toggle collapse"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path
                d="M15 6 9 12l6 6"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                className={collapsed ? 'rotate-180 origin-center' : ''}
              />
            </svg>
          </button>
        </div>

        <nav className="px-3">
          <div className="space-y-1">
            {navItems.map((item) => (
              <SidebarLink
                key={item.to}
                to={item.to}
                icon={item.icon}
                label={item.label}
                collapsed={collapsed}
                onNavigate={() => setMobileOpen(false)}
              />
            ))}
          </div>

          <div className="mt-6 border-t border-white/10 pt-4">
            <Button
              variant="danger"
              className={collapsed ? 'w-full justify-center' : 'w-full'}
              onClick={onLogout}
            >
              {collapsed ? '⎋' : 'Logout'}
            </Button>
          </div>
        </nav>
      </aside>

      {/* Main content */}
      <div className={['min-h-screen', collapsed ? 'lg:pl-20' : 'lg:pl-72'].join(' ')}>
        {/* Top bar */}
        <header className="sticky top-0 z-30 border-b border-white/10 bg-slate-950/70 backdrop-blur">
          <div className="container-page flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-200 hover:bg-white/10 lg:hidden"
                onClick={() => setMobileOpen(true)}
                aria-label="Open sidebar"
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
              <div>
                <div className="text-sm font-semibold text-white">{pageTitle}</div>
                <div className="text-xs text-slate-400">Welcome back, {user?.name}</div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden text-right sm:block">
                <div className="text-sm text-slate-200">{user?.email}</div>
                <div className="text-xs text-slate-500">Mock auth (API-ready)</div>
              </div>
              <div className="grid h-10 w-10 place-items-center rounded-full bg-white/5 ring-1 ring-white/10">
                <span className="text-xs font-semibold text-slate-200">
                  {getInitials(user?.email)}
                </span>
              </div>
            </div>
          </div>
        </header>

        <main className="container-page py-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

