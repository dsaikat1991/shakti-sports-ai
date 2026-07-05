import clsx from "clsx";

export default function Badge({ children, className = "" }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-300",
        className
      )}
    >
      {children}
    </span>
  );
}