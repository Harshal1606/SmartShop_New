import { useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { AuthShell } from '../components/auth/AuthShell.jsx'
import { Button } from '../components/ui/Button.jsx'
import { Input } from '../components/ui/Input.jsx'
import { useAuth } from '../context/AuthContext.jsx'

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || '').trim())
}

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = useMemo(() => location.state?.from?.pathname || '/dashboard', [location.state])

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setFormError('')

    const nextErrors = {}
    if (!isValidEmail(email)) nextErrors.email = 'Enter a valid email address.'
    if (!password || password.length < 6) nextErrors.password = 'Password must be at least 6 characters.'
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length) return

    setIsSubmitting(true)
    try {
      // Mock auth logic today; backend integration will replace this later.
      await login({ email, password })
      navigate(from, { replace: true })
    } catch (err) {
      setFormError(err?.message || 'Login failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Log in to view your dashboards and upload CCTV videos."
      footer={
        <>
          Don’t have an account?{' '}
          <Link to="/signup" className="text-indigo-200 hover:text-white">
            Create one
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <Input
          id="email"
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
        />

        <Input
          id="password"
          label="Password"
          type="password"
          autoComplete="current-password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
        />

        {formError ? (
          <div className="rounded-xl border border-rose-400/20 bg-rose-500/10 p-3 text-sm text-rose-200">
            {formError}
          </div>
        ) : null}

        <Button type="submit" className="w-full" isLoading={isSubmitting}>
          Login
        </Button>

        <div className="text-center text-xs text-slate-500">
          Tip: any valid email + 6+ character password will work (mock auth).
        </div>
      </form>
    </AuthShell>
  )
}

