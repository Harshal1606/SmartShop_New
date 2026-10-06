import { PlaceholderPanel } from '../components/analytics/PlaceholderPanel.jsx'
import { StatCard } from '../components/analytics/StatCard.jsx'

export function DashboardPage() {
  // Mock data (replace with API responses later)
  const stats = [
    {
      label: 'Total Visitors Today',
      value: '1,284',
      change: '+8% vs yesterday',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path
            d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
          <path
            d="M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"
            stroke="currentColor"
            strokeWidth="1.6"
          />
          <path
            d="M20 21v-2a4 4 0 0 0-3-3.87"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
          <path
            d="M17 3.13a4 4 0 0 1 0 7.75"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      ),
    },
    {
      label: 'Average Dwell Time',
      value: '4m 12s',
      change: 'Stable',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 7v5l3 2"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
            stroke="currentColor"
            strokeWidth="1.6"
          />
        </svg>
      ),
    },
    {
      label: 'Peak Hour',
      value: '6–7 PM',
      change: 'Highest traffic window',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path
            d="M4 19V5m0 14h16"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
          <path
            d="M8 15l3-3 3 2 4-6"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
    },
    {
      label: 'Conversion Estimate',
      value: '3.1%',
      change: '+0.4pp WoW',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path
            d="M4 19V5m0 14h16"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
          <path
            d="M8 16h2m2-4h2m2-4h2"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((s) => (
          <StatCard key={s.label} label={s.label} value={s.value} change={s.change} icon={s.icon} />
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <PlaceholderPanel
          title="Visitors Trend"
          subtitle="A line chart will be rendered here once the analytics API is live."
          heightClass="h-80"
        />
        <PlaceholderPanel
          title="Heatmap Preview"
          subtitle="Heatmap overlay placeholder (waiting for ML processing output)."
          heightClass="h-80"
        />
      </div>
    </div>
  )
}

