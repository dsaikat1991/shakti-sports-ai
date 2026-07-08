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
    <div className="w-full max-w-md rounded-4xl border border-gray-200 bg-white p-8 shadow-2xl shadow-gray-200/70">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        {eyebrow}
      </p>

      <h1 className="mt-3 font-['Anton'] text-4xl uppercase leading-none text-gray-950">
        {title}
      </h1>

      <p className="mt-3 text-sm leading-6 text-gray-600">{subtitle}</p>

      <div className="mt-7">{children}</div>
    </div>
  );
}