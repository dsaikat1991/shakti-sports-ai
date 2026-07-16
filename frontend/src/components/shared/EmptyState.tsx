import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: ReactNode;
  // "primary" (default) is for a genuine first-run state - nothing
  // exists yet, and there's usually an action to take. "neutral" is for
  // a search/filter yielding no results - not a call to action, so it
  // stays muted rather than sharing the same warm treatment.
  tone?: "primary" | "neutral";
  action?: ReactNode;
}

export default function EmptyState({
  icon: Icon,
  title,
  description,
  tone = "primary",
  action,
}: EmptyStateProps) {
  return (
    <div className="mt-10 rounded-4xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center">
      <div
        className={`mx-auto flex h-16 w-16 items-center justify-center rounded-full ${
          tone === "primary" ? "bg-orange-50" : "bg-gray-100"
        }`}
      >
        <Icon className={`h-7 w-7 ${tone === "primary" ? "text-[#F0600E]" : "text-gray-400"}`} />
      </div>

      <h2 className="mt-5 text-2xl font-bold text-gray-950">{title}</h2>

      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
        {description}
      </p>

      {action}
    </div>
  );
}
