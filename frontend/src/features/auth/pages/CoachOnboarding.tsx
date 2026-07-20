import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ROUTES } from "../../../constants/routes";
import {
  createBaseProfile,
  createCoachProfile,
} from "../services/profile.service";

const specializations = [
  "Sprint",
  "Hurdles",
  "Long Jump",
  "High Jump",
  "General / All-round",
];

export default function CoachOnboarding() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const [form, setForm] = useState({
    organization: "",
    designation: "",
    fullName: "",
    state: "",
    district: "",
    specialization: "",
    experienceYears: "",
    bio: "",
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
      role: "coach",
      fullName: form.fullName,
      state: form.state,
      district: form.district,
    });

    if (profileResult.error) {
      setSaving(false);
      setErrorMessage(profileResult.error.message);
      return;
    }

    const coachResult = await createCoachProfile({
      id: user.id,
      organization: form.organization,
      designation: form.designation,
      experienceYears: form.experienceYears
        ? Number(form.experienceYears)
        : undefined,
      specialization: form.specialization,
      bio: form.bio,
    });

    setSaving(false);

    if (coachResult.error) {
      setErrorMessage(coachResult.error.message);
      return;
    }

    nextStep();
  }

  return (
    <div className="w-full max-w-3xl rounded-4xl border border-border-default bg-surface-card p-8 shadow-2xl shadow-border-default/70">
      <div className="mb-8">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-brand-action">
          Build Coach Profile
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
          <h1 className="text-2xl font-bold text-text-primary md:text-3xl">
            Where do you coach?
          </h1>

          <p className="mt-4 text-base leading-7 text-text-secondary">
            This helps Shakti connect you with athletes training near you.
          </p>

          <div className="mt-8 grid gap-4">
            <input
              value={form.organization}
              onChange={(e) => updateField("organization", e.target.value)}
              placeholder="Organization / academy / club"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />

            <input
              value={form.designation}
              onChange={(e) => updateField("designation", e.target.value)}
              placeholder="Designation (e.g. Head Coach, Sprint Coach)"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <h1 className="text-2xl font-bold text-text-primary md:text-3xl">
            Tell us about you.
          </h1>

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
          <h1 className="text-2xl font-bold text-text-primary md:text-3xl">
            Your coaching background.
          </h1>

          <p className="mt-4 text-base leading-7 text-text-secondary">
            This helps athletes and academies understand your expertise.
          </p>

          <div className="mt-8 grid gap-4">
            <select
              value={form.specialization}
              onChange={(e) => updateField("specialization", e.target.value)}
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            >
              <option value="">Specialization</option>
              {specializations.map((event) => (
                <option key={event} value={event}>
                  {event}
                </option>
              ))}
            </select>

            <input
              type="number"
              min="0"
              value={form.experienceYears}
              onChange={(e) => updateField("experienceYears", e.target.value)}
              placeholder="Years of coaching experience"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />

            <textarea
              value={form.bio}
              onChange={(e) => updateField("bio", e.target.value)}
              placeholder="A short bio (optional)"
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

          <h1 className="mt-6 text-2xl font-bold text-text-primary md:text-3xl">
            Welcome to Shakti.
          </h1>

          <p className="mx-auto mt-4 max-w-md text-base leading-7 text-text-secondary">
            Your coach profile is saved. Invite athletes to connect and
            you'll be able to review their performance history and reports
            from your console.
          </p>

          <button
            type="button"
            onClick={() => navigate(ROUTES.COACH.HOME)}
            className="mt-8 cursor-pointer rounded-xl bg-brand-action px-6 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover"
          >
            Go to Coach Console →
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
