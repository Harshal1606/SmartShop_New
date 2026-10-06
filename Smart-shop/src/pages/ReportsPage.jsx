export function ReportsPage() {
  return (
    <div className="space-y-4">
      <div className="card p-6">
        <div className="text-lg font-semibold text-white">Reports</div>
        <div className="mt-1 text-sm text-slate-400">
          This section will host downloadable reports and historical analytics once the backend is
          connected.
        </div>
      </div>

      <div className="card p-6">
        <div className="text-sm font-semibold text-white">Coming soon</div>
        <ul className="mt-3 space-y-2 text-sm text-slate-400">
          <li>- Daily / weekly / monthly footfall summaries</li>
          <li>- Heatmap exports</li>
          <li>- CSV/PDF report generation</li>
        </ul>
      </div>
    </div>
  )
}

