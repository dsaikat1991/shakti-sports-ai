import type { ButtonHTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

// primary/secondary/outline are the original marketing variants - kept on
// their pre-token-system raw colors untouched (Hero.tsx, FinalCTA.tsx
// still consume them unchanged). Marketing's own migration onto tokens is
// a separate, already-queued batch - not a side effect of this change.
// brand/brand-outline/link are the new token-backed variants for Athlete
// Console consumers.
type Variant = "primary" | "secondary" | "outline" | "brand" | "brand-outline" | "link";

const BOX_VARIANTS: Variant[] = ["primary", "secondary", "outline", "brand", "brand-outline"];

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
          "bg-orange-500 text-white hover:bg-orange-600":
            variant === "primary",

          "bg-green-700 text-white hover:bg-green-800":
            variant === "secondary",

          "border border-gray-300 bg-white text-gray-900 hover:border-orange-500 hover:text-orange-600":
            variant === "outline",

          "bg-brand-action text-white hover:bg-brand-action-hover":
            variant === "brand",

          "border border-border-default text-text-secondary hover:border-text-disabled hover:text-text-primary":
            variant === "brand-outline",

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