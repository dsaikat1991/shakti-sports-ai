import {
  Building2,
  CheckCircle2,
  Loader2,
  Save,
  ShieldCheck,
  Sparkles,
  Trophy,
  User,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { useAthleteProfile } from "../hooks/useAthleteProfile";
import { useUpdateAthleteProfile } from "../hooks/useAthleteProfileMutations";

const EVENTS = ["Sprint", "Hurdles", "Long Jump", "High Jump"];

type FormState = {
  full_name: string;
  state: string;
  district: string;
  date_of_birth: string;
  gender: string;
  height_cm: string;
  weight_kg: string;
  preferred_event: string;
  secondary_event: string;
  academy: string;
  dominant_leg: string;
  bio: string;
  achievements: string;
  personal_best: string;
};

function toFormState(base: any, sporting: any): FormState {
  return {
    full_name: base?.full_name ?? "",
    state: base?.state ?? "",
    district: base?.district ?? "",
    date_of_birth: sporting?.date_of_birth ?? "",
    gender: sporting?.gender ?? "",
    height_cm: sporting?.height_cm != null ? String(sporting.height_cm) : "",
    weight_kg: sporting?.weight_kg != null ? String(sporting.weight_kg) : "",
    preferred_event: sporting?.preferred_event ?? "",
    secondary_event: sporting?.secondary_event ?? "",
    academy: sporting?.academy ?? "",
    dominant_leg: sporting?.dominant_leg ?? "",
    bio: sporting?.bio ?? "",
    achievements: sporting?.achievements ?? "",
    personal_best: sporting?.personal_best ?? "",
  };
}

function initialsFor(name: string, email: string) {
  const source = name.trim() || email;
  return source.charAt(0).toUpperCase() || "A";
}

function inputClass() {
  return "w-full rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100";
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <label className="mb-1.5 block text-xs font-bold uppercase tracking-widest text-gray-400">
      {children}
    </label>
  );
}

function ReservedCard({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Users;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-5">
      <div className="flex items-center gap-2 text-gray-400">
        <Icon className="h-4 w-4" />
        <p className="text-xs font-bold uppercase tracking-widest">{title}</p>
      </div>
      <p className="mt-2 text-sm leading-6 text-gray-500">{description}</p>
    </div>
  );
}

export default function AthleteProfile() {
  const { user } = useAuth();
  const { data, isLoading, error } = useAthleteProfile(user?.id);
  const updateProfile = useUpdateAthleteProfile(user?.id);

  const [form, setForm] = useState<FormState | null>(null);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  useEffect(() => {
    if (data) {
      setForm(toFormState(data.base, data.sporting));
    }
  }, [data]);

  function updateField(field: keyof FormState, value: string) {
    setForm((prev) => (prev ? { ...prev, [field]: value } : prev));
    setSaveMessage(null);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form) return;

    updateProfile.mutate(
      {
        base: {
          full_name: form.full_name || null,
          state: form.state || null,
          district: form.district || null,
        },
        sporting: {
          date_of_birth: form.date_of_birth || null,
          gender: form.gender || null,
          height_cm: form.height_cm ? Number(form.height_cm) : null,
          weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
          preferred_event: form.preferred_event || null,
          secondary_event: form.secondary_event || null,
          academy: form.academy || null,
          dominant_leg: form.dominant_leg || null,
          bio: form.bio || null,
          achievements: form.achievements || null,
          personal_best: form.personal_best || null,
        },
      },
      {
        onSuccess: () => setSaveMessage("Profile saved."),
      },
    );
  }

  if (isLoading || !form) {
    return (
      <div className="mx-auto max-w-4xl rounded-4xl border border-gray-200 bg-white p-10 text-center shadow-sm">
        <Loader2 className="mx-auto h-9 w-9 animate-spin text-[#F0600E]" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-4xl rounded-4xl border border-red-200 bg-red-50 p-10 text-center text-sm font-semibold text-red-700">
        {error.message}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        Profile
      </p>
      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        Your Athlete Profile
      </h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        This is the record coaches, academies, and future talent-discovery
        tools will see once you connect with them. Keep it accurate.
      </p>

      <form onSubmit={handleSubmit} className="mt-10 space-y-6">
        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-[#F0600E] text-2xl font-black text-white">
              {initialsFor(form.full_name, user?.email ?? "")}
            </div>
            <div>
              <p className="text-sm font-bold text-gray-950">
                {form.full_name || "Unnamed athlete"}
              </p>
              <p className="text-xs text-gray-500">
                Photo upload is coming soon - your initials are shown until then.
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <User className="h-5 w-5 text-[#F0600E]" />
            <h2 className="font-bold text-gray-950">Personal Information</h2>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div>
              <FieldLabel>Full name</FieldLabel>
              <input
                className={inputClass()}
                value={form.full_name}
                onChange={(e) => updateField("full_name", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel>Date of birth</FieldLabel>
              <input
                type="date"
                className={inputClass()}
                value={form.date_of_birth}
                onChange={(e) => updateField("date_of_birth", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel>Gender</FieldLabel>
              <select
                className={inputClass()}
                value={form.gender}
                onChange={(e) => updateField("gender", e.target.value)}
              >
                <option value="">Not specified</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other / Prefer not to say</option>
              </select>
            </div>
            <div>
              <FieldLabel>State</FieldLabel>
              <input
                className={inputClass()}
                value={form.state}
                onChange={(e) => updateField("state", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel>District</FieldLabel>
              <input
                className={inputClass()}
                value={form.district}
                onChange={(e) => updateField("district", e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-[#F0600E]" />
            <h2 className="font-bold text-gray-950">Sporting Information</h2>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div>
              <FieldLabel>Preferred event</FieldLabel>
              <select
                className={inputClass()}
                value={form.preferred_event}
                onChange={(e) => updateField("preferred_event", e.target.value)}
              >
                <option value="">Not specified</option>
                {EVENTS.map((event) => (
                  <option key={event} value={event}>
                    {event}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <FieldLabel>Secondary event</FieldLabel>
              <select
                className={inputClass()}
                value={form.secondary_event}
                onChange={(e) => updateField("secondary_event", e.target.value)}
              >
                <option value="">Not specified</option>
                {EVENTS.map((event) => (
                  <option key={event} value={event}>
                    {event}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <FieldLabel>Dominant side</FieldLabel>
              <select
                className={inputClass()}
                value={form.dominant_leg}
                onChange={(e) => updateField("dominant_leg", e.target.value)}
              >
                <option value="">Not specified</option>
                <option value="left">Left</option>
                <option value="right">Right</option>
                <option value="ambidextrous">Ambidextrous</option>
              </select>
            </div>
            <div>
              <FieldLabel>Academy / training centre</FieldLabel>
              <input
                className={inputClass()}
                value={form.academy}
                onChange={(e) => updateField("academy", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel>Height (cm)</FieldLabel>
              <input
                type="number"
                min="0"
                className={inputClass()}
                value={form.height_cm}
                onChange={(e) => updateField("height_cm", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel>Weight (kg)</FieldLabel>
              <input
                type="number"
                min="0"
                className={inputClass()}
                value={form.weight_kg}
                onChange={(e) => updateField("weight_kg", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel>Personal best</FieldLabel>
              <input
                className={inputClass()}
                placeholder="e.g. 11.42s (100m)"
                value={form.personal_best}
                onChange={(e) => updateField("personal_best", e.target.value)}
              />
            </div>
          </div>

          <div className="mt-4">
            <FieldLabel>Bio</FieldLabel>
            <textarea
              rows={3}
              className={inputClass()}
              value={form.bio}
              onChange={(e) => updateField("bio", e.target.value)}
            />
          </div>

          <div className="mt-4">
            <FieldLabel>Achievements</FieldLabel>
            <textarea
              rows={3}
              placeholder="State championships, records, selections..."
              className={inputClass()}
              value={form.achievements}
              onChange={(e) => updateField("achievements", e.target.value)}
            />
          </div>
        </div>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-[#F0600E]" />
            <h2 className="font-bold text-gray-950">Coaches</h2>
          </div>
          <p className="mt-2 text-sm leading-6 text-gray-600">
            Manage who can see your performances and reports from the
            dedicated Coaches page.
          </p>
          <Link
            to={ROUTES.ATHLETE.COACHES}
            className="mt-4 inline-flex items-center gap-2 text-sm font-bold text-[#F0600E] hover:text-orange-700"
          >
            Go to Coaches
          </Link>
        </div>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-[#F0600E]" />
            <h2 className="font-bold text-gray-950">Reserved for future modules</h2>
          </div>
          <p className="mt-2 text-sm text-gray-500">
            These aren't built yet - shown here so you know they're planned,
            not missing.
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <ReservedCard
              icon={ShieldCheck}
              title="Guardian"
              description="For athletes under 18, a linked guardian will be able to review and approve connections."
            />
            <ReservedCard
              icon={Building2}
              title="Organization / Federation"
              description="Academy, state, and national federation memberships will appear here once organizations exist as their own entities."
            />
            <ReservedCard
              icon={CheckCircle2}
              title="Discoverability"
              description="Control over whether coaches/scouts can find you without an existing connection - see Settings for the current placeholder."
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            type="submit"
            disabled={updateProfile.isPending}
            className="inline-flex items-center gap-2 rounded-xl bg-[#F0600E] px-6 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {updateProfile.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            Save Profile
          </button>

          {saveMessage && (
            <p className="text-sm font-semibold text-green-700">{saveMessage}</p>
          )}
          {updateProfile.isError && (
            <p className="text-sm font-semibold text-red-600">
              {(updateProfile.error as Error).message}
            </p>
          )}
        </div>
      </form>
    </div>
  );
}
