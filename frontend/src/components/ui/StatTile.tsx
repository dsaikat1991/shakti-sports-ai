import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

interface StatTileProps {
  icon: LucideIcon;
  value: ReactNode;
  label: string;
  // Color of the icon's soft circle badge - independent of the numeric
  // value's own meaning, purely a visual accent.
  tone?: "brand" | "info" | "success";
}

const TONE_STYLES: Record<NonNullable<StatTileProps["tone"]>, string> = {
  brand: "bg-brand-action-soft text-brand-action",
  info: "bg-info-insight-soft text-info-insight",
  success: "bg-success-progress-soft text-success-progress",
};

// Extracted from AthleteHome.tsx's Performance Summary card (icon-in-soft-
// circle + mono value + label) so the next stat tile is a prop, not a
// copy-paste of the same markup.
export default function StatTile({ icon: Icon, value, label, tone = "brand" }: StatTileProps) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-border-divider p-3">
      <span
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${TONE_STYLES[tone]}`}
      >
        <Icon className="h-4.5 w-4.5" />
      </span>
      <div>
        <p className="font-['JetBrains_Mono'] text-xl font-semibold text-text-primary">
          {value}
        </p>
        <p className="text-xs text-text-muted">{label}</p>
      </div>
    </div>
  );
}
