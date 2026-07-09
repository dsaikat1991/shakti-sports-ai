import WizardLayout from "../components/WizardLayout";
import type { WizardStepProps } from "../store/performanceWizard.store";
import type { PerformanceType } from "../types/performance";

const performanceTypes: {
  id: PerformanceType;
  title: string;
  description: string;
}[] = [
  {
    id: "practice",
    title: "Practice",
    description: "A regular training session to track improvement.",
  },
  {
    id: "competition",
    title: "Competition",
    description: "A race, jump, meet, or official performance.",
  },
  {
    id: "trial",
    title: "Trial",
    description: "A selection trial, academy test, or coach evaluation.",
  },
  {
    id: "assessment",
    title: "Assessment",
    description: "A technical check focused on form and movement quality.",
  },
];

export default function PerformanceTypeStep({
  wizard,
  setWizard,
  nextStep,
  previousStep,
}: WizardStepProps) {
  const selectedType = wizard.draft.performanceType;

  function selectType(type: PerformanceType) {
    setWizard((prev) => ({
      ...prev,
      draft: {
        ...prev.draft,
        performanceType: type,
      },
    }));
  }

  return (
    <WizardLayout
      step={2}
      totalSteps={5}
      title="What kind of session is this?"
      description="This helps Shakti compare the performance in the right context."
    >
      <div className="grid gap-4 md:grid-cols-2">
        {performanceTypes.map((type) => {
          const isActive = selectedType === type.id;

          return (
            <button
              key={type.id}
              type="button"
              onClick={() => selectType(type.id)}
              className={`cursor-pointer rounded-3xl border p-6 text-left transition duration-300 hover:-translate-y-1 ${
                isActive
                  ? "border-[#F0600E] bg-[#FFF8F3] shadow-xl shadow-orange-100"
                  : "border-gray-200 bg-white hover:border-orange-300"
              }`}
            >
              <p className="font-['Anton'] text-3xl uppercase text-gray-950">
                {type.title}
              </p>

              <p className="mt-3 text-sm leading-6 text-gray-600">
                {type.description}
              </p>
            </button>
          );
        })}
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
          disabled={!selectedType}
          className="cursor-pointer rounded-xl bg-[#F0600E] px-6 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Continue →
        </button>
      </div>
    </WizardLayout>
  );
}