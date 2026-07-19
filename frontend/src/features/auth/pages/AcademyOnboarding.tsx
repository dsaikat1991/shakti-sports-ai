import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ROUTES } from "../../../constants/routes";
import {
  createAcademyProfile,
  createBaseProfile,
} from "../services/profile.service";

export default function AcademyOnboarding() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const [form, setForm] = useState({
    academyName: "",
    website: "",
    fullName: "",
    state: "",
    district: "",
    address: "",
    description: "",
  });

  function updateField(field: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function nextStep() {
    setStep((prev) => Math.min(prev + 1, 4));
  }

  function prevStep() {
    setStep((prev) => Math.max(prev - 1, 1));
  }

  async function completeOnboarding() {
    if (!user) {
      setErrorMessage("You must be signed in to complete onboarding.");
      return;
    }

    setSaving(true);
    setErrorMessage("");

    const profileResult = await createBaseProfile({
      id: user.id,
      email: user.email ?? "",
      role: "academy",
      fullName: form.fullName,
      state: form.state,
      district: form.district,
    });

    if (profileResult.error) {
      setSaving(false);
      setErrorMessage(profileResult.error.message);
      return;
    }

    const academyResult = await createAcademyProfile({
      id: user.id,
      academyName: form.academyName,
      website: form.website,
      address: form.address,
      description: form.description,
    });

    setSaving(false);

    if (academyResult.error) {
      setErrorMessage(academyResult.error.message);
      return;
    }

    nextStep();
  }

  return (
    <div className="w-full max-w-3xl rounded-4xl border border-border-default bg-surface-card p-8 shadow-2xl shadow-border-default/70">
      <div className="mb-8">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-brand-action">
          Build Academy Profile
        </p>

        <div className="mt-5 flex gap-2">
          {[1, 2, 3, 4].map((item) => (
            <div
              key={item}
              className={`h-2 flex-1 rounded-full ${
                item <= step ? "bg-brand-action" : "bg-border-default"
              }`}
            />
          ))}
        </div>

        <p className="mt-3 text-xs font-semibold uppercase tracking-widest text-text-disabled">
          Step {Math.min(step, 4)} of 4
        </p>
      </div>

      {step === 1 && (
        <div>
          <h1 className="font-['Anton'] text-4xl uppercase leading-none text-text-primary md:text-5xl">
            Tell us about your academy.
          </h1>

          <div className="mt-8 grid gap-4">
            <input
              value={form.academyName}
              onChange={(e) => updateField("academyName", e.target.value)}
              placeholder="Academy name"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />

            <input
              value={form.website}
              onChange={(e) => updateField("website", e.target.value)}
              placeholder="Website (optional)"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <h1 className="font-['Anton'] text-4xl uppercase leading-none text-text-primary md:text-5xl">
            Who should we contact?
          </h1>

          <p className="mt-4 text-base leading-7 text-text-secondary">
            The primary contact for your academy on Shakti.
          </p>

          <div className="mt-8 grid gap-4">
            <input
              value={form.fullName}
              onChange={(e) => updateField("fullName", e.target.value)}
              placeholder="Full name"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />

            <input
              value={form.state}
              onChange={(e) => updateField("state", e.target.value)}
              placeholder="State"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />

            <input
              value={form.district}
              onChange={(e) => updateField("district", e.target.value)}
              placeholder="District"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <h1 className="font-['Anton'] text-4xl uppercase leading-none text-text-primary md:text-5xl">
            Where are you located?
          </h1>

          <div className="mt-8 grid gap-4">
            <input
              value={form.address}
              onChange={(e) => updateField("address", e.target.value)}
              placeholder="Address"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />

            <textarea
              value={form.description}
              onChange={(e) => updateField("description", e.target.value)}
              placeholder="A short description of your academy (optional)"
              rows={3}
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="text-center">
          <p className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-action text-2xl font-black text-white">
            ✓
          </p>

          <h1 className="mt-6 font-['Anton'] text-4xl uppercase leading-none text-text-primary md:text-5xl">
            Welcome to Shakti.
          </h1>

          <p className="mx-auto mt-4 max-w-md text-base leading-7 text-text-secondary">
            Your academy profile is saved. Invite athletes to connect and
            you'll be able to review their performance history and reports
            from your console.
          </p>

          <button
            type="button"
            onClick={() => navigate(ROUTES.ACADEMY.HOME)}
            className="mt-8 cursor-pointer rounded-xl bg-brand-action px-6 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover"
          >
            Go to Academy Console →
          </button>
        </div>
      )}

      {step < 4 && (
        <div className="mt-10 flex items-center justify-between">
          <button
            type="button"
            onClick={prevStep}
            disabled={step === 1 || saving}
            className="cursor-pointer rounded-xl border border-border-default px-5 py-3 text-sm font-bold text-text-secondary transition hover:border-text-disabled disabled:cursor-not-allowed disabled:opacity-40"
          >
            Back
          </button>

          <button
            type="button"
            onClick={step === 3 ? completeOnboarding : nextStep}
            disabled={saving}
            className="cursor-pointer rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {step === 3
              ? saving
                ? "Saving..."
                : "Finish →"
              : "Continue →"}
          </button>
        </div>
      )}

      {errorMessage && (
        <p className="mt-4 rounded-xl bg-error-failure-soft px-4 py-3 text-sm font-semibold text-error-failure">
          {errorMessage}
        </p>
      )}
    </div>
  );
}
