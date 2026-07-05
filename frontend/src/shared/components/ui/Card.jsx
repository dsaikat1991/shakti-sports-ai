import clsx from "clsx";

export default function Card({ children, className = "" }) {
  return (
    <div
      className={clsx(
        "rounded-3xl border border-white/10 bg-[#0B1224] p-6",
        className
      )}
    >
      {children}
    </div>
  );
}