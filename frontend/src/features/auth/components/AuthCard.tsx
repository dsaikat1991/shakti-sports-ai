import type { ReactNode } from "react";

type Props = {
  eyebrow: string;
  title: string;
  subtitle: string;
  children: ReactNode;
};

export default function AuthCard({
  eyebrow,
  title,
  subtitle,
  children,
}: Props) {
  return (
    <div className="w-full max-w-md rounded-4xl border border-border-default bg-surface-card p-8 shadow-2xl shadow-border-default/70">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
        {eyebrow}
      </p>

      <h1 className="mt-3 text-2xl font-bold text-text-primary">
        {title}
      </h1>

      <p className="mt-3 text-sm leading-6 text-text-secondary">{subtitle}</p>

      <div className="mt-7">{children}</div>
    </div>
  );
}