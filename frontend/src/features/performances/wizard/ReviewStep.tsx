import { useNavigate } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";

import WizardLayout from "../components/WizardLayout";
import { EVENTS } from "../data/events";
import { PERFORMANCE_TYPES } from "../data/performanceTypes";
import { useCreatePerformance } from "../hooks/useCreatePerformance";

import type { WizardStepProps } from "../store/performanceWizard.store";

export default function ReviewStep({
  wizard,
  previousStep,
}: WizardStepProps) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const createPerformance = useCreatePerformance();

  const { event, performanceType, performedOn, title, notes, recording } =
    wizard.draft;

  const selectedEvent = EVENTS.find((item) => item.id === event);

  const selectedType = PERFORMANCE_TYPES.find(
    (item) => item.id === performanceType,
  );

  async function handleCreatePerformance() {
    if (!user) return;

const performance = await createPerformance.mutateAsync({
  athleteId: user.id,
  draft: wizard.draft,
});

navigate(
  ROUTES.ATHLETE.PERFORMANCE_PROCESSING(performance.id)
);
  }

  return (
    <WizardLayout
      step={5}
      totalSteps={5}
      title="Ready to analyze."
      description="Review your performance details before we prepare it for Shakti Motion Intelligence™."
    >
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
          <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
            Event
          </p>
          <p className="mt-2 text-xl font-bold text-gray-950">
            {selectedEvent?.title ?? "Not selected"}
          </p>
        </div>

        <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
          <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
            Session Type
          </p>
          <p className="mt-2 text-xl font-bold text-gray-950">
            {selectedType?.title ?? "Not selected"}
          </p>
        </div>

        <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
          <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
            Date
          </p>
          <p className="mt-2 text-xl font-bold text-gray-950">{performedOn}</p>
        </div>

        <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
          <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
            Recording
          </p>
          <p className="mt-2 truncate text-xl font-bold text-gray-950">
            {recording?.name ?? "No recording"}
          </p>
        </div>
      </div>

      <div className="mt-4 rounded-3xl border border-gray-200 bg-white p-5">
        <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
          Session Name
        </p>

        <p className="mt-2 text-xl font-bold text-gray-950">{title}</p>

        {notes && (
          <>
            <p className="mt-5 font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
              Notes
            </p>

            <p className="mt-2 text-sm leading-6 text-gray-600">{notes}</p>
          </>
        )}
      </div>

      <div className="mt-6 rounded-3xl border border-orange-200 bg-[#FFF8F3] p-5">
        <p className="text-sm font-bold text-gray-950">
          Next step: Shakti Motion Intelligence™
        </p>

        <p className="mt-2 text-sm leading-6 text-gray-600">
          Your recording will be uploaded securely and saved as a performance.
          AI analysis will be connected in the next stage.
        </p>
      </div>

      {createPerformance.error && (
        <p className="mt-5 rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
          {createPerformance.error.message}
        </p>
      )}

      <div className="mt-8 flex items-center justify-between">
        <button
          type="button"
          onClick={previousStep}
          disabled={createPerformance.isPending}
          className="cursor-pointer rounded-xl border border-gray-200 px-6 py-3 text-sm font-bold text-gray-700 transition hover:border-gray-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          ← Back
        </button>

        <button
          type="button"
          onClick={handleCreatePerformance}
          disabled={createPerformance.isPending}
          className="cursor-pointer rounded-xl bg-[#F0600E] px-6 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {createPerformance.isPending
            ? "Creating..."
            : "Create Performance →"}
        </button>
      </div>
    </WizardLayout>
  );
}