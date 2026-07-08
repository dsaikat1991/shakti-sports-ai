import type { WizardStepProps } from "../store/performanceWizard.store";

export default function PerformanceTypeStep(_props: WizardStepProps) {
  return (
    <div>
      <h1 className="font-['Anton'] text-5xl uppercase">
        What type of performance?
      </h1>
    </div>
  );
}