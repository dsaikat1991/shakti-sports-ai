import { ArrowLeft, Loader2, Plus, Users, X } from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import {
  useAddListMember,
  useAthleteLists,
  useListMembers,
  useRemoveListMember,
} from "../hooks/useAthleteLists";
import { usePartnerConnections } from "../hooks/usePartnerConnections";
import { getConnectionViewState } from "../lib/getConnectionViewState";

export default function PartnerListDetail() {
  const { listId } = useParams();
  const { user, role } = useAuth();
  const isAcademy = role === "academy";
  const routeSet = isAcademy ? ROUTES.ACADEMY : ROUTES.COACH;

  const { data: lists = [] } = useAthleteLists(user?.id);
  const list = lists.find((l) => l.id === listId);

  const { data: members = [], isLoading, error } = useListMembers(listId);
  const { data: connections = [] } = usePartnerConnections(user?.id);
  const addMember = useAddListMember(listId);
  const removeMember = useRemoveListMember(listId);

  const [selectedAthleteId, setSelectedAthleteId] = useState("");

  const connectedAthletes = user
    ? connections.filter((c) => getConnectionViewState(c, user.id) === "connected")
    : [];

  const memberAthleteIds = new Set(members.map((m) => m.athlete_id));
  const nameByAthleteId = new Map(
    connectedAthletes.map((c) => [c.athlete_id, c.athleteProfile?.full_name ?? "Athlete"]),
  );

  const availableToAdd = useMemo(
    () => connectedAthletes.filter((c) => !memberAthleteIds.has(c.athlete_id)),
    [connectedAthletes, members],
  );

  function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedAthleteId) return;
    addMember.mutate(selectedAthleteId, { onSuccess: () => setSelectedAthleteId("") });
  }

  return (
    <div className="mx-auto max-w-4xl">
      <Link
        to={routeSet.LISTS}
        className="inline-flex items-center gap-2 text-sm font-bold text-text-secondary transition hover:text-brand-action"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Lists
      </Link>

      <div className="mt-6">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
          {list?.list_type.replace(/_/g, " ") ?? "List"}
        </p>
        <h1 className="mt-3 text-2xl font-bold text-text-primary md:text-3xl">
          {list?.name ?? "Loading..."}
        </h1>
      </div>

      <form
        onSubmit={handleAdd}
        className="mt-8 flex flex-col gap-3 rounded-3xl border border-border-default bg-surface-card p-4 shadow-sm sm:flex-row sm:items-center"
      >
        <select
          value={selectedAthleteId}
          onChange={(e) => setSelectedAthleteId(e.target.value)}
          className="flex-1 rounded-xl border border-border-default px-3 py-2.5 text-sm outline-none focus:border-brand-action"
        >
          <option value="">
            {availableToAdd.length === 0 ? "No connected athletes left to add" : "Choose a connected athlete..."}
          </option>
          {availableToAdd.map((c) => (
            <option key={c.athlete_id} value={c.athlete_id}>
              {c.athleteProfile?.full_name ?? "Athlete"}
            </option>
          ))}
        </select>

        <button
          type="submit"
          disabled={!selectedAthleteId || addMember.isPending}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand-action px-5 py-2.5 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Plus className="h-4 w-4" />
          Add to List
        </button>
      </form>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-border-default bg-surface-card p-6 text-sm font-semibold text-text-secondary shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-brand-action" />
          Loading members...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-error-failure bg-error-failure-soft p-6 text-sm font-semibold text-error-failure">
          {error.message}
        </div>
      )}

      {!isLoading && !error && members.length === 0 && (
        <div className="mt-10 rounded-4xl border border-dashed border-border-default bg-surface-sunken p-10 text-center">
          <Users className="mx-auto h-11 w-11 text-text-disabled" />
          <h2 className="mt-5 text-2xl font-bold text-text-primary">No athletes on this list yet</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-text-muted">
            Add a connected athlete above.
          </p>
        </div>
      )}

      {!isLoading && members.length > 0 && (
        <div className="mt-8 space-y-3">
          {members.map((member) => {
            const stillConnected = memberAthleteIds.has(member.athlete_id) &&
              connectedAthletes.some((c) => c.athlete_id === member.athlete_id);

            return (
              <div
                key={member.id}
                className="flex items-center justify-between rounded-3xl border border-border-default bg-surface-card p-5 shadow-sm"
              >
                <div>
                  <p className="font-bold text-text-primary">
                    {nameByAthleteId.get(member.athlete_id) ?? "Athlete"}
                  </p>
                  {!stillConnected && (
                    <p className="mt-1 text-xs font-semibold text-warning-attention">
                      No longer connected - profile/report access has ended
                    </p>
                  )}
                </div>

                <button
                  type="button"
                  onClick={() => removeMember.mutate(member.id)}
                  disabled={removeMember.isPending}
                  className="flex h-9 w-9 items-center justify-center rounded-xl border border-border-default text-text-muted transition hover:border-error-failure hover:text-error-failure disabled:opacity-50"
                  aria-label="Remove from list"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
