import WizardLayout from "../components/WizardLayout";
import type { WizardStepProps } from "../store/performanceWizard.store";

const dateOptions = [
  {
    label: "Today",
    value: new Date().toISOString().split("T")[0],
  },
  {
    label: "Yesterday",
    value: new Date(Date.now() - 86400000).toISOString().split("T")[0],
  },
];

export default function DetailsStep({
  wizard,
  setWizard,
  nextStep,
  previousStep,
}: WizardStepProps) {
  const { title, notes, performedOn } = wizard.draft;

  function updateDraft(field: "title" | "notes" | "performedOn", value: string) {
    setWizard((prev) => ({
      ...prev,
      draft: {
        ...prev.draft,
        [field]: value,
      },
    }));
  }

  return (
    <WizardLayout
      step={3}
      totalSteps={5}
      title="Tell us about this performance."
      description="Add a date, and a personal note if you want one - we'll take care of naming the session."
    >
      <div>
        <p className="text-sm font-bold text-gray-950">
          When did this performance happen?
        </p>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          {dateOptions.map((option) => {
            const isActive = performedOn === option.value;

            return (
              <button
                key={option.label}
                type="button"
                onClick={() => updateDraft("performedOn", option.value)}
                className={`cursor-pointer rounded-2xl border px-5 py-4 text-left transition hover:-translate-y-1 ${
                  isActive
                    ? "border-[#F0600E] bg-[#FFF8F3] shadow-lg shadow-orange-100"
                    : "border-gray-200 bg-white hover:border-orange-300"
                }`}
              >
                <span className="text-sm font-bold text-gray-950">
                  {option.label}
                </span>
                <span className="mt-1 block font-['JetBrains_Mono'] text-[10px] uppercase tracking-widest text-gray-400">
                  {option.value}
                </span>
              </button>
            );
          })}

          <input
            type="date"
            value={performedOn}
            onChange={(event) => updateDraft("performedOn", event.target.value)}
            className="rounded-2xl border border-gray-200 px-5 py-4 text-sm font-bold text-gray-950 outline-none transition focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
          />
        </div>
      </div>

      <div className="mt-7 grid gap-4">
        <div>
          <label className="text-sm font-bold text-gray-950">
            Personal note
            <span className="font-medium text-gray-400"> optional</span>
          </label>

          <input
            value={title}
            onChange={(event) => updateDraft("title", event.target.value)}
            placeholder="Felt amazing today"
            className="mt-2 w-full rounded-2xl border border-gray-200 px-5 py-4 text-sm outline-none transition focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
          />
        </div>

        <div>
          <label className="text-sm font-bold text-gray-950">
            Additional notes
            <span className="font-medium text-gray-400"> optional</span>
          </label>

          <textarea
            value={notes}
            onChange={(event) => updateDraft("notes", event.target.value)}
            placeholder="How did it feel? Any wind, surface, injury, or coach feedback?"
            rows={4}
            className="mt-2 w-full resize-none rounded-2xl border border-gray-200 px-5 py-4 text-sm outline-none transition focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
          />
        </div>
      </div>

      <div className="mt-8 flex items-center justify-between">
        <button
          type="button"
          onClick={previousStep}
          className="cursor-pointer rounded-xl border border-gray-200 px-6 py-3 text-sm font-bold text-gray-700 transition hover:border-gray-400"
        >
          ← Back
        </button>

        <button
          type="button"
          onClick={nextStep}
          disabled={!performedOn}
          className="cursor-pointer rounded-xl bg-[#F0600E] px-6 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Continue →
        </button>
      </div>
    </WizardLayout>
  );
}