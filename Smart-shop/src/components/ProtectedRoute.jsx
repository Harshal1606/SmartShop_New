import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { FullPageLoader } from './feedback/FullPageLoader.jsx'

/**
 * Route guard for authenticated areas.
 * If not logged in -> redirect to /login, preserving "from" location.
 */
export function ProtectedRoute() {
  const { isAuthenticated, isBootstrapping } = useAuth()
  const location = useLocation()

  if (isBootstrapping) return <FullPageLoader label="Loading your workspace..." />

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}

