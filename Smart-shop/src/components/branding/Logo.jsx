export function Logo({ className = '' }) {
  return (
    <div className={['flex items-center gap-2', className].join(' ')}>
      <div className="grid h-9 w-9 place-items-center rounded-xl bg-indigo-500/15 ring-1 ring-indigo-400/30">
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="text-indigo-200"
        >
          <path
            d="M4 7.5c0-.8.7-1.5 1.5-1.5h13c.8 0 1.5.7 1.5 1.5V18c0 .8-.7 1.5-1.5 1.5h-13C4.7 19.5 4 18.8 4 18V7.5Z"
            stroke="currentColor"
            strokeWidth="1.6"
          />
          <path
            d="M8 16v-5m4 5v-8m4 8v-3"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      </div>
      <div className="leading-tight">
        <div className="text-sm font-semibold text-slate-100">Smart Shop</div>
        <div className="text-xs text-slate-400">Analytics</div>
      </div>
    </div>
  )
}

