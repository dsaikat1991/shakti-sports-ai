import { UploadCloud, Video } from "lucide-react";
import WizardLayout from "../components/WizardLayout";
import type { WizardStepProps } from "../store/performanceWizard.store";

export default function UploadStep({
  wizard,
  setWizard,
  nextStep,
  previousStep,
}: WizardStepProps) {
  const recording = wizard.draft.recording;

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];

    if (!file) return;

    setWizard((prev) => ({
      ...prev,
      draft: {
        ...prev.draft,
        recording: file,
      },
    }));
  }

  return (
    <WizardLayout
      step={4}
      totalSteps={5}
      title="Upload your recording."
      description="Use a clear side-view recording where your full body stays visible throughout the performance."
    >
      <label
        htmlFor="recording"
        className={`block cursor-pointer rounded-4xl border-2 border-dashed p-10 text-center transition hover:border-[#F0600E] hover:bg-orange-50/40 ${
          recording
            ? "border-[#F0600E] bg-[#FFF8F3]"
            : "border-gray-300 bg-gray-50"
        }`}
      >
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-white shadow-sm">
          {recording ? (
            <Video className="h-8 w-8 text-[#F0600E]" />
          ) : (
            <UploadCloud className="h-8 w-8 text-gray-500" />
          )}
        </div>

        <h3 className="mt-5 text-xl font-bold text-gray-950">
          {recording ? recording.name : "Choose performance recording"}
        </h3>

        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
          MP4, MOV, or WEBM recommended. Keep the athlete fully visible and avoid shaky camera movement.
        </p>

        <input
          id="recording"
          type="file"
          accept="video/mp4,video/quicktime,video/webm"
          onChange={handleFileChange}
          className="hidden"
        />
      </label>

      <div className="mt-6 grid gap-3 rounded-3xl border border-gray-200 bg-white p-5 sm:grid-cols-3">
        <div>
          <p className="text-sm font-bold text-gray-950">Camera</p>
          <p className="mt-1 text-sm text-gray-500">Side view preferred</p>
        </div>

        <div>
          <p className="text-sm font-bold text-gray-950">Frame</p>
          <p className="mt-1 text-sm text-gray-500">Full body visible</p>
        </div>

        <div>
          <p className="text-sm font-bold text-gray-950">Lighting</p>
          <p className="mt-1 text-sm text-gray-500">Clear and stable</p>
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
          disabled={!recording}
          className="cursor-pointer rounded-xl bg-[#F0600E] px-6 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Continue →
        </button>
      </div>
    </WizardLayout>
  );
}