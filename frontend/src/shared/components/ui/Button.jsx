import clsx from "clsx";

export default function Button({
  children,
  variant = "primary",
  size = "md",
  className = "",
  ...props
}) {
  const variants = {
    primary:
      "bg-cyan-500 text-white hover:bg-cyan-400 focus:ring-cyan-400/40",
    secondary:
      "border border-white/10 bg-white/5 text-white hover:bg-white/10 focus:ring-white/20",
    ghost:
      "text-slate-300 hover:bg-white/5 hover:text-white focus:ring-white/20",
  };

  const sizes = {
    sm: "px-4 py-2 text-sm",
    md: "px-5 py-3 text-sm",
    lg: "px-7 py-4 text-base",
  };

  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded-2xl font-semibold transition-all duration-300 hover:-translate-y-0.5 focus:outline-none focus:ring-4 active:scale-95",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}