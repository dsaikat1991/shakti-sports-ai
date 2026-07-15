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
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        Requests
      </p>

      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        Connect With Athletes
      </h1>

      <form
        onSubmit={handleInvite}
        className="mt-10 rounded-4xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <h2 className="text-lg font-bold text-gray-950">Invite an athlete</h2>
        <p className="mt-1 text-sm text-gray-500">
          Enter the email address the athlete signed up with. They'll need to
          accept before you can see any of their data.
        </p>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Mail className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="athlete@example.com"
              className="w-full rounded-xl border border-gray-300 py-3 pl-11 pr-4 text-sm focus:border-[#F0600E] focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={requestConnection.isPending}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {requestConnection.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Send Invite
          </button>
        </div>

        {formError && <p className="mt-3 text-sm font-semibold text-red-600">{formError}</p>}
        {formSuccess && (
          <p className="mt-3 text-sm font-semibold text-green-700">{formSuccess}</p>
        )}
      </form>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading requests...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-700">
          {error.message}
        </div>
      )}

      {!isLoading && incoming.length > 0 && (
        <div className="mt-10">
          <h2 className="text-lg font-bold text-gray-950">Waiting on your response</h2>

          <div className="mt-4 space-y-3">
            {incoming.map((connection) => (
              <div
                key={connection.id}
                className="flex items-center justify-between rounded-3xl border border-gray-200 bg-white p-5 shadow-sm"
              >
                <div>
                  <p className="font-bold text-gray-950">
                    {connection.athleteProfile?.full_name ?? "An athlete"}
                  </p>
                  <p className="mt-1 text-sm text-gray-500">
                    {connection.athleteProfile?.email ?? ""}
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    type="button"
                    disabled={respond.isPending}
                    onClick={() => respond.mutate({ connectionId: connection.id, status: "accepted" })}
                    className="inline-flex items-center gap-1 rounded-xl bg-[#F0600E] px-4 py-2 text-sm font-bold text-white transition hover:bg-orange-700 disabled:opacity-50"
                  >
                    <Check className="h-4 w-4" />
                    Accept
                  </button>
                  <button
                    type="button"
                    disabled={respond.isPending}
                    onClick={() => respond.mutate({ connectionId: connection.id, status: "rejected" })}
                    className="inline-flex items-center gap-1 rounded-xl border border-gray-300 px-4 py-2 text-sm font-bold text-gray-700 transition hover:border-red-300 hover:text-red-600 disabled:opacity-50"
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
          <h2 className="text-lg font-bold text-gray-950">Sent, awaiting a response</h2>

          <div className="mt-4 space-y-3">
            {outgoing.map((connection) => (
              <div
                key={connection.id}
                className="flex items-center justify-between rounded-3xl border border-gray-200 bg-white p-5 shadow-sm"
              >
                <div>
                  <p className="font-bold text-gray-950">
                    {connection.athleteProfile?.full_name ?? connection.invited_email ?? "An athlete"}
                  </p>
                  <p className="mt-1 text-sm text-gray-500">
                    {connection.athleteProfile?.email ?? connection.invited_email ?? ""}
                  </p>
                </div>

                <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-bold text-[#F0600E]">
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
