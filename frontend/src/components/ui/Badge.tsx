import type { ReactNode } from "react";
import clsx from "clsx";

export type BadgeVariant = "success" | "info" | "warning" | "fair" | "error" | "neutral" | "brand";
type Size = "pill" | "chip";

interface Props {
  children: ReactNode;
  variant?: BadgeVariant;
  // "pill" - the original marketing badge shape. "chip" - the compact
  // mono/uppercase treatment Athlete Console's rating/status badges use.
  size?: Size;
  className?: string;
}

const VARIANT_BG: Record<BadgeVariant, string> = {
  success: "bg-success-progress-soft",
  info: "bg-info-insight-soft",
  warning: "bg-warning-attention-soft",
  fair: "bg-rating-fair-soft",
  error: "bg-error-failure-soft",
  neutral: "bg-surface-sunken",
  brand: "bg-brand-action-soft",
};

const VARIANT_TEXT: Record<BadgeVariant, string> = {
  success: "text-success-progress",
  info: "text-info-insight",
  warning: "text-warning-attention",
  fair: "text-rating-fair",
  error: "text-error-failure",
  neutral: "text-text-secondary",
  brand: "text-brand-action",
};

const SIZE_STYLES: Record<Size, string> = {
  pill: "rounded-full px-4 py-2 text-xs font-semibold uppercase tracking-wider",
  chip: "rounded-md px-2.5 py-1 font-['JetBrains_Mono'] text-[10.5px] font-medium uppercase tracking-[0.04em]",
};

export default function Badge({
  children,
  variant = "success",
  size = "pill",
  className,
}: Props) {
  // Pill-size "success" keeps a darker text shade so this stays
  // byte-for-byte identical to the component's pre-token-system look
  // (Hero.tsx's badge - the old green-700 hex equals success-progress-
  // hover). Chip-size "success" already shipped with the lighter base
  // shade (RatingBadge's Excellent, verified earlier this session) - kept
  // as its own case rather than unified, since changing either now would
  // be a visible regression somewhere already confirmed correct.
  const textClass =
    variant === "success" && size === "pill"
      ? "text-success-progress-hover"
      : VARIANT_TEXT[variant];

  return (
    <span
      className={clsx(
        "inline-flex w-fit items-center",
        VARIANT_BG[variant],
        textClass,
        SIZE_STYLES[size],
        className,
      )}
    >
      {children}
    </span>
  );
}
