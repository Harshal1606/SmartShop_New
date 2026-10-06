export function Input({
  label,
  hint,
  error,
  className = '',
  inputClassName = '',
  id,
  ...props
}) {
  const describedBy = [
    hint ? `${id}-hint` : null,
    error ? `${id}-error` : null,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={className}>
      {label ? (
        <label htmlFor={id} className="mb-1 block text-sm font-medium text-slate-200">
          {label}
        </label>
      ) : null}

      <input
        id={id}
        className={[
          'h-11 w-full rounded-xl border bg-slate-950/40 px-3 text-sm text-slate-100',
          'border-white/10 placeholder:text-slate-500',
          'focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-400/20',
          error ? 'border-rose-400/50 focus:border-rose-400/70 focus:ring-rose-400/15' : '',
          inputClassName,
        ].join(' ')}
        aria-invalid={Boolean(error)}
        aria-describedby={describedBy || undefined}
        {...props}
      />

      {hint ? (
        <div id={`${id}-hint`} className="mt-1 text-xs text-slate-400">
          {hint}
        </div>
      ) : null}

      {error ? (
        <div id={`${id}-error`} className="mt-1 text-xs text-rose-300">
          {error}
        </div>
      ) : null}
    </div>
  )
}

