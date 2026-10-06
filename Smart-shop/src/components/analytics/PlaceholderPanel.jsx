export function PlaceholderPanel({ title, subtitle, heightClass = 'h-72' }) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm font-semibold text-white">{title}</div>
          {subtitle ? <div className="mt-1 text-xs text-slate-400">{subtitle}</div> : null}
        </div>
        <div className="text-xs text-slate-500">Mock</div>
      </div>

      <div
        className={[
          'mt-4 w-full rounded-xl border border-dashed border-white/15 bg-gradient-to-br from-white/5 to-transparent',
          heightClass,
        ].join(' ')}
      >
        <div className="flex h-full w-full items-center justify-center">
          <div className="text-sm text-slate-500">Chart/Visualization placeholder</div>
        </div>
      </div>
    </div>
  )
}

