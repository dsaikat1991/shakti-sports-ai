import { Check, Loader2, Mail, X } from "lucide-react";
import { useState } from "react";

import { useAuth } from "../../auth/context/AuthContext";
import { useRequestConnection, useRespondToConnection } from "../hooks/useConnectionActions";
import { usePartnerConnections } from "../hooks/usePartnerConnections";
import { getConnectionViewState } from "../lib/getConnectionViewState";

export default function PartnerRequests() {
  const { user } = useAuth();
  const [email, setEmail] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  const { data: connections = [], isLoading, error } = usePartnerConnections(user?.id);
  const requestConnection = useRequestConnection();
  const respond = useRespondToConnection();

  const incoming = user
    ? connections.filter((c) => getConnectionViewState(c, user.id) === "incoming_request")
    : [];
  const outgoing = user
    ? connections.filter((c) => getConnectionViewState(c, user.id) === "outgoing_request")
    : [];

  function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    setFormSuccess(null);

    if (!email.trim()) return;

    requestConnection.mutate(email.trim(), {
      onSuccess: () => {
        setFormSuccess(`Invitation sent to ${email.trim()}.`);
        setEmail("");
      },
      onError: (err) => {
        setFormError(err.message || "Could not send that invitation.");
      },
    });
  }

  return (
    <div className="mx-auto max-w-4xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
        Requests
      </p>

      <h1 className="mt-3 text-2xl font-bold text-text-primary md:text-3xl">
        Connect With Athletes
      </h1>

      <form
        onSubmit={handleInvite}
        className="mt-10 rounded-4xl border border-border-default bg-surface-card p-6 shadow-sm"
      >
        <h2 className="text-lg font-bold text-text-primary">Invite an athlete</h2>
        <p className="mt-1 text-sm text-text-muted">
          Enter the email address the athlete signed up with. They'll need to
          accept before you can see any of their data.
        </p>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Mail className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-text-disabled" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="athlete@example.com"
              className="w-full rounded-xl border border-border-default py-3 pl-11 pr-4 text-sm focus:border-brand-action focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={requestConnection.isPending}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {requestConnection.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Send Invite
          </button>
        </div>

        {formError && <p className="mt-3 text-sm font-semibold text-error-failure">{formError}</p>}
        {formSuccess && (
          <p className="mt-3 text-sm font-semibold text-success-progress">{formSuccess}</p>
        )}
      </form>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-border-default bg-surface-card p-6 text-sm font-semibold text-text-secondary shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-brand-action" />
          Loading requests...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-error-failure bg-error-failure-soft p-6 text-sm font-semibold text-error-failure">
          {error.message}
        </div>
      )}

      {!isLoading && incoming.length > 0 && (
        <div className="mt-10">
          <h2 className="text-lg font-bold text-text-primary">Waiting on your response</h2>

          <div className="mt-4 space-y-3">
            {incoming.map((connection) => (
              <div
                key={connection.id}
                className="flex items-center justify-between rounded-3xl border border-border-default bg-surface-card p-5 shadow-sm"
              >
                <div>
                  <p className="font-bold text-text-primary">
                    {connection.athleteProfile?.full_name ?? "An athlete"}
                  </p>
                  <p className="mt-1 text-sm text-text-muted">
                    {connection.athleteProfile?.email ?? ""}
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    type="button"
                    disabled={respond.isPending}
                    onClick={() => respond.mutate({ connectionId: connection.id, status: "accepted" })}
                    className="inline-flex items-center gap-1 rounded-xl bg-brand-action px-4 py-2 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:opacity-50"
                  >
                    <Check className="h-4 w-4" />
                    Accept
                  </button>
                  <button
                    type="button"
                    disabled={respond.isPending}
                    onClick={() => respond.mutate({ connectionId: connection.id, status: "rejected" })}
                    className="inline-flex items-center gap-1 rounded-xl border border-border-default px-4 py-2 text-sm font-bold text-text-secondary transition hover:border-error-failure hover:text-error-failure disabled:opacity-50"
                  >
                    <X className="h-4 w-4" />
                    Decline
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!isLoading && outgoing.length > 0 && (
        <div className="mt-10">
          <h2 className="text-lg font-bold text-text-primary">Sent, awaiting a response</h2>

          <div className="mt-4 space-y-3">
            {outgoing.map((connection) => (
              <div
                key={connection.id}
                className="flex items-center justify-between rounded-3xl border border-border-default bg-surface-card p-5 shadow-sm"
              >
                <div>
                  <p className="font-bold text-text-primary">
                    {connection.athleteProfile?.full_name ?? connection.invited_email ?? "An athlete"}
                  </p>
                  <p className="mt-1 text-sm text-text-muted">
                    {connection.athleteProfile?.email ?? connection.invited_email ?? ""}
                  </p>
                </div>

                <span className="rounded-full bg-brand-action-soft px-3 py-1 text-xs font-bold text-brand-action">
                  Pending
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
