import clsx from "clsx";

export default function GlassCard({ children, className = "" }) {
  return (
    <div
      className={clsx(
        "rounded-3xl border border-white/10 bg-white/5 p-6 shadow-[0_0_60px_rgba(34,211,238,0.08)] backdrop-blur-xl",
        className
      )}
    >
      {children}
    </div>
  );
}