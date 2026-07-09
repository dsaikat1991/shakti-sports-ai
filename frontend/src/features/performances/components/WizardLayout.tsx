import type { ReactNode } from "react";

type Props = {
  step: number;
  totalSteps: number;
  title: string;
  description: string;
  children: ReactNode;
};

export default function WizardLayout({
  step,
  totalSteps,
  title,
  description,
  children,
}: Props) {
  return (
    <div className="rounded-4xl border border-gray-200 bg-white p-8 shadow-2xl shadow-gray-200/70">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
        Start New Performance
      </p>

      <div className="mt-5 flex gap-2">
        {Array.from({ length: totalSteps }).map((_, index) => {
          const currentStep = index + 1;

          return (
            <div
              key={currentStep}
              className={`h-2 flex-1 rounded-full ${
                currentStep <= step ? "bg-[#F0600E]" : "bg-gray-200"
              }`}
            />
          );
        })}
      </div>

      <p className="mt-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
        Step {step} of {totalSteps}
      </p>

      <h1 className="mt-8 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        {title}
      </h1>

      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        {description}
      </p>

      <div className="mt-8">{children}</div>
    </div>
  );
}