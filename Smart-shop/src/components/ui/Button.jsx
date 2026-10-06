import { Spinner } from '../feedback/Spinner.jsx'

const VARIANTS = {
  primary:
    'bg-indigo-500 text-white hover:bg-indigo-400 focus-visible:outline-indigo-400',
  secondary:
    'bg-white/10 text-white hover:bg-white/15 focus-visible:outline-white/30',
  ghost:
    'bg-transparent text-white hover:bg-white/10 focus-visible:outline-white/30',
  danger:
    'bg-rose-500/90 text-white hover:bg-rose-500 focus-visible:outline-rose-400',
}

const SIZES = {
  sm: 'h-9 px-3 text-sm',
  md: 'h-11 px-4 text-sm',
  lg: 'h-12 px-5 text-base',
}

export function Button({
  as: Comp = 'button',
  variant = 'primary',
  size = 'md',
  className = '',
  isLoading = false,
  disabled,
  children,
  ...props
}) {
  const isDisabled = Boolean(disabled || isLoading)

  return (
    <Comp
      className={[
        'inline-flex items-center justify-center gap-2 rounded-xl font-medium transition',
        'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2',
        'disabled:cursor-not-allowed disabled:opacity-60',
        VARIANTS[variant] || VARIANTS.primary,
        SIZES[size] || SIZES.md,
        className,
      ].join(' ')}
      disabled={Comp === 'button' ? isDisabled : undefined}
      aria-disabled={Comp !== 'button' ? isDisabled : undefined}
      {...props}
    >
      {isLoading ? <Spinner className="h-4 w-4 border-t-white" /> : null}
      <span>{children}</span>
    </Comp>
  )
}

