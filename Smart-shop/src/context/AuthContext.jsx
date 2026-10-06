import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const STORAGE_KEY = 'ssa_user'

const AuthContext = createContext(null)

function getInitialUser() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

/**
 * AuthProvider
 * - Backend is not ready, so this uses mock async auth.
 * - Keeps a persisted user in localStorage for better UX during refreshes.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isBootstrapping, setIsBootstrapping] = useState(true)

  useEffect(() => {
    // Bootstrap auth state on first load
    const existing = getInitialUser()
    setUser(existing)
    setIsBootstrapping(false)
  }, [])

  useEffect(() => {
    try {
      if (user) localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
      else localStorage.removeItem(STORAGE_KEY)
    } catch {
      // ignore storage failures (private mode / disabled storage)
    }
  }, [user])

  const login = async ({ email }) => {
    // Mock latency
    await new Promise((r) => setTimeout(r, 700))
    const name = String(email || '').split('@')[0] || 'User'
    setUser({ email, name })
    return { ok: true }
  }

  const signup = async ({ email }) => {
    // Mock latency
    await new Promise((r) => setTimeout(r, 900))
    const name = String(email || '').split('@')[0] || 'User'
    setUser({ email, name })
    return { ok: true }
  }

  const logout = () => setUser(null)

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isBootstrapping,
      login,
      signup,
      logout,
    }),
    [user, isBootstrapping],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

