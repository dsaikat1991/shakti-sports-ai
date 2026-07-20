import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ROUTES } from "../../../constants/routes";
import {
  createAthleteProfile,
  createBaseProfile,
} from "../services/profile.service";

const events = ["Sprint", "Hurdles", "Long Jump", "High Jump"];

export default function AthleteOnboarding() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const [form, setForm] = useState({
    event: "",
    fullName: "",
    dob: "",
    gender: "",
    state: "",
    district: "",
    academy: "",
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
      role: "athlete",
      fullName: form.fullName,
      state: form.state,
      district: form.district,
    });

    if (profileResult.error) {
      setSaving(false);
      setErrorMessage(profileResult.error.message);
      return;
    }

    const athleteResult = await createAthleteProfile({
      id: user.id,
      dateOfBirth: form.dob,
      gender: form.gender,
      preferredEvent: form.event,
      academy: form.academy,
    });

    setSaving(false);

    if (athleteResult.error) {
      setErrorMessage(athleteResult.error.message);
      return;
    }

    navigate(ROUTES.ATHLETE.HOME);
  }

  return (
    <div className="w-full max-w-3xl rounded-4xl border border-border-default bg-surface-card p-8 shadow-2xl shadow-border-default/70">
      <div className="mb-8">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-brand-action">
          Build Athlete Profile
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
          Step {step} of 4
        </p>
      </div>

      {step === 1 && (
        <div>
          <h1 className="text-2xl font-bold text-text-primary md:text-3xl">
            Which event do you compete in?
          </h1>

          <p className="mt-4 text-base leading-7 text-text-secondary">
            Start with your primary performance. You can add more events later.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {events.map((event) => (
              <button
                key={event}
                type="button"
                onClick={() => updateField("event", event)}
                className={`cursor-pointer rounded-2xl border p-5 text-left transition duration-300 hover:-translate-y-1 ${
                  form.event === event
                    ? "border-brand-action bg-brand-action-tint shadow-xl shadow-brand-action-soft"
                    : "border-border-default bg-surface-card hover:border-brand-action-soft"
                }`}
              >
                <p className="text-xl font-bold text-text-primary">{event}</p>
                <p className="mt-2 text-sm text-text-muted">
                  Shakti Motion Intelligence supported.
                </p>
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <h1 className="text-2xl font-bold text-text-primary md:text-3xl">
            Nice. Let’s build your profile.
          </h1>

          <div className="mt-8 grid gap-4">
            <input
              value={form.fullName}
              onChange={(e) => updateField("fullName", e.target.value)}
              placeholder="Full name"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />

            <input
              type="date"
              value={form.dob}
              onChange={(e) => updateField("dob", e.target.value)}
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />

            <select
              value={form.gender}
              onChange={(e) => updateField("gender", e.target.value)}
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            >
              <option value="">Gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other / Prefer not to say</option>
            </select>
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <h1 className="text-2xl font-bold text-text-primary md:text-3xl">
            Where do you train?
          </h1>

          <p className="mt-4 text-base leading-7 text-text-secondary">
            This helps coaches discover athletes by region and event.
          </p>

          <div className="mt-8 grid gap-4">
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

            <input
              value={form.academy}
              onChange={(e) => updateField("academy", e.target.value)}
              placeholder="Academy / training centre optional"
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
            Your athlete profile is ready. Next, we’ll help you start your first
            performance and generate your first AI report.
          </p>
        </div>
      )}

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
          onClick={step === 4 ? completeOnboarding : nextStep}
          disabled={(step === 1 && !form.event) || saving}
          className="cursor-pointer rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {step === 4
            ? saving
              ? "Saving..."
              : "Go to Athlete Console →"
            : "Continue →"}
        </button>
      </div>

      {errorMessage && (
        <p className="mt-4 rounded-xl bg-error-failure-soft px-4 py-3 text-sm font-semibold text-error-failure">
          {errorMessage}
        </p>
      )}
    </div>
  );
}