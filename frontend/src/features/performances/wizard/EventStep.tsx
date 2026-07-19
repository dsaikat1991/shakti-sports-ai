import WizardLayout from "../components/WizardLayout";
import { EVENTS } from "../data/events";

import type { WizardStepProps } from "../store/performanceWizard.store";
import type { PerformanceEvent } from "../types/performance";

export default function EventStep({
  wizard,
  setWizard,
  nextStep,
}: WizardStepProps) {
  const selectedEvent = wizard.draft.event;

  function selectEvent(event: PerformanceEvent) {
    setWizard((prev) => ({
      ...prev,
      draft: {
        ...prev.draft,
        event,
      },
    }));
  }

  return (
    <WizardLayout
      step={1}
      totalSteps={5}
      title="What are you training today?"
      description="Choose the performance event Shakti Motion Intelligence™ should analyze."
    >
      <div className="grid gap-4 md:grid-cols-2">
        {EVENTS.map((event) => {
          const isActive = selectedEvent === event.id;

          return (
            <button
              key={event.id}
              type="button"
              onClick={() => selectEvent(event.id)}
              className={`cursor-pointer rounded-3xl border p-6 text-left transition duration-300 hover:-translate-y-1 ${
                isActive
                  ? "border-[#F0600E] bg-[#FFF8F3] shadow-xl shadow-orange-100"
                  : "border-gray-200 bg-white hover:border-orange-300"
              }`}
            >
              <p className="text-lg font-bold text-gray-950">
                {event.title}
              </p>

              <p className="mt-2 text-sm font-bold text-[#F0600E]">
                {event.subtitle}
              </p>

              <p className="mt-3 text-sm leading-6 text-gray-600">
                {event.description}
              </p>
            </button>
          );
        })}
      </div>

      <div className="mt-8 flex justify-end">
        <button
          type="button"
          onClick={nextStep}
          disabled={!selectedEvent}
          className="cursor-pointer rounded-xl bg-[#F0600E] px-6 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Continue →
        </button>
      </div>
    </WizardLayout>
  );
}