import type { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

export default function Badge({ children }: Props) {
  return (
    <span className="inline-flex items-center rounded-full bg-green-100 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-green-700">
      {children}
    </span>
  );
}