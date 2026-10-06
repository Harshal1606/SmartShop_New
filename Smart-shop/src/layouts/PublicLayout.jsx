import { Outlet } from 'react-router-dom'
import { Footer } from '../components/nav/Footer.jsx'
import { Navbar } from '../components/nav/Navbar.jsx'

export function PublicLayout() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}

