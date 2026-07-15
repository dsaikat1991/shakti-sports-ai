import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  createAcademyProfile,
  createBaseProfile,
} from "../services/profile.service";

export default function AcademyOnboarding() {
  const { user, signOut } = useAuth();

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
    <div className="w-full max-w-3xl rounded-4xl border border-gray-200 bg-white p-8 shadow-2xl shadow-gray-200/70">
      <div className="mb-8">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
          Build Academy Profile
        </p>

        <div className="mt-5 flex gap-2">
          {[1, 2, 3, 4].map((item) => (
            <div
              key={item}
              className={`h-2 flex-1 rounded-full ${
                item <= step ? "bg-[#F0600E]" : "bg-gray-200"
              }`}
            />
          ))}
        </div>

        <p className="mt-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
          Step {Math.min(step, 4)} of 4
        </p>
      </div>

      {step === 1 && (
        <div>
          <h1 className="font-['Anton'] text-4xl uppercase leading-none text-gray-950 md:text-5xl">
            Tell us about your academy.
          </h1>

          <div className="mt-8 grid gap-4">
            <input
              value={form.academyName}
              onChange={(e) => updateField("academyName", e.target.value)}
              placeholder="Academy name"
              className="rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
            />

            <input
              value={form.website}
              onChange={(e) => updateField("website", e.target.value)}
              placeholder="Website (optional)"
              className="rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
            />
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <h1 className="font-['Anton'] text-4xl uppercase leading-none text-gray-950 md:text-5xl">
            Who should we contact?
          </h1>

          <p className="mt-4 text-base leading-7 text-gray-600">
            The primary contact for your academy on Shakti.
          </p>

          <div className="mt-8 grid gap-4">
            <input
              value={form.fullName}
              onChange={(e) => updateField("fullName", e.target.value)}
              placeholder="Full name"
              className="rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
            />

            <input
              value={form.state}
              onChange={(e) => updateField("state", e.target.value)}
              placeholder="State"
              className="rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
            />

            <input
              value={form.district}
              onChange={(e) => updateField("district", e.target.value)}
              placeholder="District"
              className="rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
            />
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <h1 className="font-['Anton'] text-4xl uppercase leading-none text-gray-950 md:text-5xl">
            Where are you located?
          </h1>

          <div className="mt-8 grid gap-4">
            <input
              value={form.address}
              onChange={(e) => updateField("address", e.target.value)}
              placeholder="Address"
              className="rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
            />

            <textarea
              value={form.description}
              onChange={(e) => updateField("description", e.target.value)}
              placeholder="A short description of your academy (optional)"
              rows={3}
              className="rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
            />
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="text-center">
          <p className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[#F0600E] text-2xl font-black text-white">
            ✓
          </p>

          <h1 className="mt-6 font-['Anton'] text-4xl uppercase leading-none text-gray-950 md:text-5xl">
            Welcome to Shakti.
          </h1>

          <p className="mx-auto mt-4 max-w-md text-base leading-7 text-gray-600">
            Your academy profile is saved. The full academy console —
            squad management, progress tracking, and reports — is still
            being built. We'll notify you the moment it's ready.
          </p>

          <button
            type="button"
            onClick={signOut}
            className="mt-8 cursor-pointer rounded-xl border border-gray-200 px-6 py-3 text-sm font-bold text-gray-700 transition hover:border-gray-400"
          >
            Sign Out
          </button>
        </div>
      )}

      {step < 4 && (
        <div className="mt-10 flex items-center justify-between">
          <button
            type="button"
            onClick={prevStep}
            disabled={step === 1 || saving}
            className="cursor-pointer rounded-xl border border-gray-200 px-5 py-3 text-sm font-bold text-gray-700 transition hover:border-gray-400 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Back
          </button>

          <button
            type="button"
            onClick={step === 3 ? completeOnboarding : nextStep}
            disabled={saving}
            className="cursor-pointer rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
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
        <p className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
          {errorMessage}
        </p>
      )}
    </div>
  );
}
