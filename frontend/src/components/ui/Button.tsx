import type { ButtonHTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

// primary/outline are Hero.tsx/FinalCTA.tsx's marketing CTAs - now on the
// token system (Marketing's migration batch). "secondary" (green) has no
// real consumer anywhere in the app today - tokenized for consistency
// with the "no raw hex" rule anyway; its hover shade is the same as its
// base (no darker green token exists) since there's nothing to verify it
// against. "link" is the text-only variant used by Athlete Console.
type Variant = "primary" | "secondary" | "outline" | "link";

const BOX_VARIANTS: Variant[] = ["primary", "secondary", "outline"];

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: Variant;
}

export default function Button({
  children,
  variant = "primary",
  className,
  ...props
}: ButtonProps) {
  const isBox = BOX_VARIANTS.includes(variant);

  return (
    <button
      {...props}
      className={clsx(
        "inline-flex cursor-pointer items-center justify-center transition-all duration-200",
        isBox && "rounded-lg px-6 py-3 text-sm font-semibold",
        {
          "bg-brand-action text-white hover:bg-brand-action-hover":
            variant === "primary",

          "bg-success-progress-hover text-white hover:bg-success-progress-hover":
            variant === "secondary",

          "border border-border-default bg-surface-card text-text-primary hover:border-brand-action hover:text-brand-action":
            variant === "outline",

          "text-sm font-medium text-brand-action hover:text-brand-action-hover":
            variant === "link",
        },
        className
      )}
    >
      {children}
    </button>
  );
}
