import type { WizardStepProps } from "../store/performanceWizard.store";

export default function EventStep(_props: WizardStepProps) {
  return (
    <div>
      <h1 className="font-['Anton'] text-5xl uppercase">
        What are you training today?
      </h1>
    </div>
  );
}