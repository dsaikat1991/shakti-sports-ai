import { useState } from "react";

import EventStep from "./EventStep";
import PerformanceTypeStep from "./PerformanceTypeStep";
import DetailsStep from "./DetailsStep";
import UploadStep from "./UploadStep";
import ReviewStep from "./ReviewStep";

import { initialWizardState } from "../store/performanceWizard.store";

export default function Wizard() {

  const [wizard, setWizard] = useState(initialWizardState);

  function nextStep() {
    setWizard((prev) => ({
      ...prev,
      step: Math.min(prev.step + 1, 5),
    }));
  }

  function previousStep() {
    setWizard((prev) => ({
      ...prev,
      step: Math.max(prev.step - 1, 1),
    }));
  }

  switch (wizard.step) {
    case 1:
      return (
        <EventStep
          wizard={wizard}
          setWizard={setWizard}
          nextStep={nextStep}
        />
      );

    case 2:
      return (
        <PerformanceTypeStep
          wizard={wizard}
          setWizard={setWizard}
          nextStep={nextStep}
          previousStep={previousStep}
        />
      );

    case 3:
      return (
        <DetailsStep
          wizard={wizard}
          setWizard={setWizard}
          nextStep={nextStep}
          previousStep={previousStep}
        />
      );

    case 4:
      return (
        <UploadStep
          wizard={wizard}
          setWizard={setWizard}
          nextStep={nextStep}
          previousStep={previousStep}
        />
      );

    default:
      return (
        <ReviewStep
          wizard={wizard}
          setWizard={setWizard}
          nextStep={nextStep}
          previousStep={previousStep}
  />
);
  }
}