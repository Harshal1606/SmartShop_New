export function FeatureCard({ title, description, icon }) {
  return (
    <div className="card card-hover p-6">
      <div className="flex items-start gap-4">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-indigo-500/15 ring-1 ring-indigo-400/30">
          {icon}
        </div>
        <div>
          <div className="text-base font-semibold text-white">{title}</div>
          <div className="mt-2 text-sm text-slate-400">{description}</div>
        </div>
      </div>
    </div>
  )
}

