import type { ButtonHTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

type Variant = "primary" | "secondary" | "outline";

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
  return (
    <button
      {...props}
      className={clsx(
        "inline-flex cursor-pointer items-center justify-center rounded-lg px-6 py-3 text-sm font-semibold transition-all duration-200",
        {
          "bg-orange-500 text-white hover:bg-orange-600":
            variant === "primary",

          "bg-green-700 text-white hover:bg-green-800":
            variant === "secondary",

          "border border-gray-300 bg-white text-gray-900 hover:border-orange-500 hover:text-orange-600":
            variant === "outline",
        },
        className
      )}
    >
      {children}
    </button>
  );
}