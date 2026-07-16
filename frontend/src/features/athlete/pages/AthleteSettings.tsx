import {
  AlertTriangle,
  Building2,
  Eye,
  KeyRound,
  Loader2,
  Save,
  ShieldCheck,
  Sparkles,
  Trash2,
  Users,
} from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { changePassword } from "../../auth/services/auth.service";
import { useAthleteConnections } from "../../partners/hooks/useAthleteConnections";
import { getConnectionViewState } from "../../partners/lib/getConnectionViewState";
import { useAthleteProfile } from "../hooks/useAthleteProfile";
import {
  useSetAccountDeletionRequested,
  useUpdateAiTrainingConsent,
} from "../hooks/useAthleteProfileMutations";

function SettingsCard({
  icon: Icon,
  title,
  description,
  children,
}: {
  icon: typeof Users;
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-center gap-2">
        <Icon className="h-5 w-5 text-[#F0600E]" />
        <h2 className="font-bold text-gray-950">{title}</h2>
      </div>
      {description && <p className="mt-2 text-sm leading-6 text-gray-600">{description}</p>}
      <div className="mt-4">{children}</div>
    </div>
  );
}

function ReservedCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-5">
      <p className="text-xs font-bold uppercase tracking-widest text-gray-400">{title}</p>
      <p className="mt-2 text-sm leading-6 text-gray-500">{description}</p>
    </div>
  );
}

function PasswordSection() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [status, setStatus] = useState<{ type: "success" | "error"; message: string } | null>(
    null,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus(null);

    if (password.length < 6) {
      setStatus({ type: "error", message: "Password must be at least 6 characters." });
      return;
    }
    if (password !== confirmPassword) {
      setStatus({ type: "error", message: "Passwords don't match." });
      return;
    }

    setIsSubmitting(true);
    const { error } = await changePassword(password);
    setIsSubmitting(false);

    if (error) {
      setStatus({ type: "error", message: error.message });
      return;
    }

    setPassword("");
    setConfirmPassword("");
    setStatus({ type: "success", message: "Password updated." });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="New password"
        className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
      />
      <input
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        placeholder="Confirm new password"
        className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
      />
      <button
        type="submit"
        disabled={isSubmitting || !password}
        className="inline-flex items-center gap-2 rounded-xl bg-[#F0600E] px-5 py-2.5 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
        Update Password
      </button>
      {status && (
        <p className={`text-sm font-semibold ${status.type === "success" ? "text-green-700" : "text-red-600"}`}>
          {status.message}
        </p>
      )}
    </form>
  );
}

export default function AthleteSettings() {
  const { user } = useAuth();
  const { data: profileData } = useAthleteProfile(user?.id);
  const { data: connections = [] } = useAthleteConnections(user?.id);

  const updateConsent = useUpdateAiTrainingConsent(user?.id);
  const setDeletionRequested = useSetAccountDeletionRequested(user?.id);

  const [confirmingDelete, setConfirmingDelete] = useState(false);

  const connectedOrgs = user
    ? connections.filter((c) => getConnectionViewState(c, user.id) === "connected")
    : [];

  const consent = profileData?.sporting?.ai_training_consent ?? false;
  const deletionRequested = Boolean(profileData?.sporting?.deletion_requested_at);

  return (
    <div className="mx-auto max-w-3xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        Settings
      </p>
      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        Account Settings
      </h1>

      <div className="mt-10 space-y-6">
        <SettingsCard
          icon={Users}
          title="Profile"
          description="Personal and sporting information."
        >
          <Link
            to={ROUTES.ATHLETE.PROFILE}
            className="inline-flex items-center gap-2 text-sm font-bold text-[#F0600E] hover:text-orange-700"
          >
            Edit your profile
          </Link>
        </SettingsCard>

        <SettingsCard icon={KeyRound} title="Password">
          <PasswordSection />
        </SettingsCard>

        <SettingsCard
          icon={Eye}
          title="Privacy"
          description="Control over who can see your data."
        >
          <ReservedCard
            title="Discoverability"
            description="Letting coaches/scouts find you without an existing connection is planned but not built yet - your data stays private to you and any coach you've explicitly connected with."
          />
        </SettingsCard>

        <SettingsCard
          icon={Sparkles}
          title="AI Model Training Consent"
          description="Whether your uploaded footage and derived data may be used to improve Shakti's AI models. This is separate from using the platform itself - opting out doesn't affect your reports."
        >
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={consent}
              disabled={updateConsent.isPending}
              onChange={(e) => updateConsent.mutate(e.target.checked)}
              className="h-5 w-5 rounded border-gray-300 text-[#F0600E] focus:ring-[#F0600E]"
            />
            <span className="text-sm font-semibold text-gray-800">
              I consent to my data being used for AI model training
            </span>
          </label>
        </SettingsCard>

        <SettingsCard
          icon={Building2}
          title="Connected Organizations"
          description="Coaches and academies with access to your performances."
        >
          {connectedOrgs.length === 0 ? (
            <p className="text-sm text-gray-500">
              No connections yet -{" "}
              <Link to={ROUTES.ATHLETE.COACHES} className="font-bold text-[#F0600E] hover:text-orange-700">
                connect with a coach
              </Link>
              .
            </p>
          ) : (
            <ul className="space-y-2">
              {connectedOrgs.map((c) => (
                <li key={c.id} className="flex items-center gap-2 text-sm font-semibold text-gray-800">
                  <ShieldCheck className="h-4 w-4 text-green-700" />
                  {c.partnerProfile?.full_name ?? "Connected account"}
                  <span className="text-gray-400">
                    ({c.partner_role === "academy" ? "Academy" : "Coach"})
                  </span>
                </li>
              ))}
            </ul>
          )}
        </SettingsCard>

        <SettingsCard
          icon={ShieldCheck}
          title="Guardian"
        >
          <ReservedCard
            title="Guardian access"
            description="For athletes under 18, a linked guardian will be able to review connection requests and consent decisions. Not built yet."
          />
        </SettingsCard>

        <div className="rounded-4xl border border-red-200 bg-red-50 p-6">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-700" />
            <h2 className="font-bold text-red-900">Delete Account</h2>
          </div>
          <p className="mt-2 text-sm leading-6 text-red-700">
            This records a request for our team to review and action manually
            - it does not delete your data immediately. There's no automatic
            self-service deletion yet, since that needs to be done carefully
            given everything tied to your account (performances, reports,
            coach connections).
          </p>

          {deletionRequested ? (
            <div className="mt-4 flex items-center gap-3">
              <p className="text-sm font-bold text-red-900">
                Deletion requested. Our team will follow up.
              </p>
              <button
                type="button"
                onClick={() => setDeletionRequested.mutate(false)}
                disabled={setDeletionRequested.isPending}
                className="text-sm font-bold text-red-700 underline hover:text-red-900 disabled:opacity-50"
              >
                Withdraw request
              </button>
            </div>
          ) : confirmingDelete ? (
            <div className="mt-4 flex items-center gap-3">
              <button
                type="button"
                onClick={() => {
                  setDeletionRequested.mutate(true);
                  setConfirmingDelete(false);
                }}
                disabled={setDeletionRequested.isPending}
                className="inline-flex items-center gap-2 rounded-xl bg-red-600 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-red-700 disabled:opacity-50"
              >
                <Trash2 className="h-4 w-4" />
                Yes, request deletion
              </button>
              <button
                type="button"
                onClick={() => setConfirmingDelete(false)}
                className="text-sm font-bold text-gray-700 hover:text-gray-900"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setConfirmingDelete(true)}
              className="mt-4 inline-flex items-center gap-2 rounded-xl border border-red-300 px-5 py-2.5 text-sm font-bold text-red-700 transition hover:bg-red-100"
            >
              <Trash2 className="h-4 w-4" />
              Request Account Deletion
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
