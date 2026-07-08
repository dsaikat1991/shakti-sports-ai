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

export const initialWizardState: WizardState = {
  step: 1,
  draft: {
    title: "",
    notes: "",
    recording: null,
  },
};