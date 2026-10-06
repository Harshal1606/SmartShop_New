import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { FeatureCard } from '../components/marketing/FeatureCard.jsx'
import { Button } from '../components/ui/Button.jsx'

export function LandingPage() {
  const { isAuthenticated } = useAuth()

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-24 left-1/2 h-72 w-[700px] -translate-x-1/2 rounded-full bg-indigo-500/20 blur-3xl" />
          <div className="absolute bottom-[-140px] right-[-120px] h-72 w-72 rounded-full bg-fuchsia-500/10 blur-3xl" />
        </div>

        <div className="container-page relative py-16 sm:py-20">
          <div className="mx-auto max-w-3xl text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-300">
              <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-emerald-200 ring-1 ring-emerald-400/25">
                API-ready
              </span>
              <span>Mock data until backend is ready</span>
            </div>

            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              Smart Shop Analytics
            </h1>
            <p className="mt-4 text-lg text-slate-300">
              AI-powered CCTV Insights for Retail Intelligence
            </p>

            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link to={isAuthenticated ? '/dashboard' : '/login'}>
                <Button variant="secondary" size="lg">
                  Login
                </Button>
              </Link>
              <Link to={isAuthenticated ? '/dashboard' : '/signup'}>
                <Button variant="primary" size="lg">
                  Get Started
                </Button>
              </Link>
            </div>

            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              <div className="card p-4 text-left">
                <div className="text-sm font-semibold text-white">Plug-in ML models</div>
                <div className="mt-1 text-sm text-slate-400">
                  Swap or upgrade models without changing UI flows.
                </div>
              </div>
              <div className="card p-4 text-left">
                <div className="text-sm font-semibold text-white">Real-time dashboards</div>
                <div className="mt-1 text-sm text-slate-400">
                  Track footfall, dwell time, peak hours, and more.
                </div>
              </div>
              <div className="card p-4 text-left">
                <div className="text-sm font-semibold text-white">Secure by default</div>
                <div className="mt-1 text-sm text-slate-400">
                  Protected routes and auth state management included.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="container-page py-16">
        <div className="flex flex-col gap-2">
          <div className="text-sm font-semibold text-indigo-200">Features</div>
          <h2 className="text-2xl font-semibold text-white sm:text-3xl">
            Analytics built for retail operators
          </h2>
          <p className="max-w-2xl text-sm text-slate-400">
            Upload CCTV footage, process it with ML (backend coming), and review insights in a
            clean, responsive dashboard.
          </p>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <FeatureCard
            title="Footfall Detection"
            description="Measure visitor counts, trends, and peak periods across time windows."
            icon={
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M8 20v-8m4 8V4m4 16v-5"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              </svg>
            }
          />
          <FeatureCard
            title="Customer Heatmaps"
            description="Visualize high-traffic zones to optimize layouts and promotions."
            icon={
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 21s7-4.5 7-11a7 7 0 1 0-14 0c0 6.5 7 11 7 11Z"
                  stroke="currentColor"
                  strokeWidth="1.6"
                />
                <path
                  d="M12 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"
                  fill="currentColor"
                  opacity="0.9"
                />
              </svg>
            }
          />
          <FeatureCard
            title="Behavior Analytics"
            description="Understand dwell time, queueing, and engagement signals."
            icon={
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M4 19c2.5-2.5 4.5-3 8-3s5.5.5 8 3"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                />
                <path
                  d="M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"
                  stroke="currentColor"
                  strokeWidth="1.6"
                />
              </svg>
            }
          />
        </div>
      </section>

      {/* About */}
      <section id="about" className="container-page pb-16">
        <div className="card p-8">
          <div className="grid gap-8 md:grid-cols-2 md:items-center">
            <div>
              <div className="text-sm font-semibold text-indigo-200">Designed for scale</div>
              <h3 className="mt-2 text-2xl font-semibold text-white">
                Modular frontend, easy backend integration
              </h3>
              <p className="mt-3 text-sm text-slate-400">
                This project is structured with reusable components, route protection, and an
                Axios client ready for your ML pipeline endpoints.
              </p>
              <div className="mt-5 flex gap-2">
                <Link to={isAuthenticated ? '/dashboard' : '/login'}>
                  <Button variant="secondary">Go to Dashboard</Button>
                </Link>
                <a href="#features">
                  <Button variant="ghost">View Features</Button>
                </a>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-indigo-500/10 via-white/5 to-transparent p-6">
              <div className="text-sm font-semibold text-white">What you’ll connect later</div>
              <ul className="mt-3 space-y-2 text-sm text-slate-300">
                <li className="flex gap-2">
                  <span className="text-emerald-300">•</span> Video upload pipeline
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-300">•</span> Model inference + processing status
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-300">•</span> Analytics API for dashboard cards
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-300">•</span> Heatmap & reporting exports
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

