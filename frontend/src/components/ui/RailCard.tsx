import type { ReactNode } from "react";
import clsx from "clsx";

interface RailCardProps {
  children: ReactNode;
  // "sunken" - a highlighted/warm-tinted card (Personal Best, Current
  // Goal). "card" (default) - a plain white card (My Progress,
  // Notifications, Performance Summary). Same border either way - the
  // distinction is background only, matching the three-tier neutral
  // system in DESIGN_BIBLE.md §4.
  tone?: "card" | "sunken";
  className?: string;
}

export default function RailCard({ children, tone = "card", className }: RailCardProps) {
  return (
    <div
      className={clsx(
        "rounded-2xl border border-border-default p-5",
        tone === "sunken" ? "bg-surface-sunken" : "bg-surface-card",
        className,
      )}
    >
      {children}
    </div>
  );
}
