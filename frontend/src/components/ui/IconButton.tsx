import type { LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";
import clsx from "clsx";

interface IconButtonProps {
  icon: LucideIcon;
  label: string;
  className?: string;
  // A small dot in the top-right corner - e.g. "you have unread
  // notifications." Real state only, never decorative.
  hasIndicator?: boolean;
  // Pass `to` for navigation (renders a react-router Link) or `onClick`
  // for an in-place action (renders a <button>) - not both.
  to?: string;
  onClick?: () => void;
  // Button mode only (e.g. a dropdown trigger) - ignored in link mode.
  ariaExpanded?: boolean;
}

// Extracted from AthleteLayout.tsx's navbar (Upload, Notifications,
// mobile-menu-toggle buttons all previously hand-copied this exact
// h-10 w-10 rounded-xl border treatment three times).
export default function IconButton({
  icon: Icon,
  label,
  className,
  hasIndicator,
  to,
  onClick,
  ariaExpanded,
}: IconButtonProps) {
  const classes = clsx(
    "relative flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-xl border border-border-default text-text-secondary transition hover:border-text-disabled hover:text-text-primary",
    className,
  );

  const content = (
    <>
      <Icon className="h-4.5 w-4.5" />
      {hasIndicator && (
        <span className="absolute right-2 top-2 h-2 w-2 rounded-full border border-surface-card bg-error-failure" />
      )}
    </>
  );

  if (to) {
    return (
      <Link to={to} aria-label={label} className={classes}>
        {content}
      </Link>
    );
  }

  return (
    <button
      type="button"
      aria-label={label}
      aria-expanded={ariaExpanded}
      onClick={onClick}
      className={classes}
    >
      {content}
    </button>
  );
}
