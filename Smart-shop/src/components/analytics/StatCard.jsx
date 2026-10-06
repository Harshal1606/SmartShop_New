export function StatCard({ label, value, change, icon }) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
            {label}
          </div>
          <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
          {change ? <div className="mt-2 text-sm text-slate-400">{change}</div> : null}
        </div>
        <div className="grid h-11 w-11 place-items-center rounded-2xl bg-white/5 ring-1 ring-white/10">
          {icon}
        </div>
      </div>
    </div>
  )
}

