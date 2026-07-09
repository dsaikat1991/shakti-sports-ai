import type { Dispatch, SetStateAction } from "react";
import type { PerformanceDraft } from "../types/performance";

export interface WizardState {
  step: number;
  draft: PerformanceDraft;
}

export interface WizardStepProps {
  wizard: WizardState;
  setWizard: Dispatch<SetStateAction<WizardState>>;
  nextStep: () => void;
  previousStep?: () => void;
}

function today() {
  return new Date().toISOString().split("T")[0];
}

export const initialWizardState: WizardState = {
  step: 1,
  draft: {
    performedOn: today(),
    title: "",
    notes: "",
    recording: null,
  },
  
};