import { ArrowRight, Loader2, Users } from "lucide-react";
import { Link } from "react-router-dom";

import EmptyState from "../../../components/shared/EmptyState";
import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { usePartnerConnections } from "../hooks/usePartnerConnections";
import { getConnectionViewState } from "../lib/getConnectionViewState";

export default function PartnerRoster() {
  const { user, role } = useAuth();
  const isAcademy = role === "academy";
  const routeSet = isAcademy ? ROUTES.ACADEMY : ROUTES.COACH;

  const { data: connections = [], isLoading, error } = usePartnerConnections(user?.id);

  const connected = user
    ? connections.filter((c) => getConnectionViewState(c, user.id) === "connected")
    : [];

  return (
    <div className="mx-auto max-w-6xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
        {isAcademy ? "Squad" : "My Athletes"}
      </p>

      <h1 className="mt-3 text-2xl font-bold text-text-primary md:text-3xl">
        Connected Athletes
      </h1>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-border-default bg-surface-card p-6 text-sm font-semibold text-text-secondary shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-brand-action" />
          Loading your athletes...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-error-failure bg-error-failure-soft p-6 text-sm font-semibold text-error-failure">
          {error.message}
        </div>
      )}

      {!isLoading && !error && connected.length === 0 && (
        <EmptyState
          icon={Users}
          title="No connected athletes yet"
          description="Once an athlete accepts your connection request, they'll appear here with their performance history."
          action={
            <Link
              to={routeSet.REQUESTS}
              className="mt-6 inline-flex items-center justify-center gap-2 rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover"
            >
              Invite an Athlete
            </Link>
          }
        />
      )}

      {!isLoading && connected.length > 0 && (
        <div className="mt-10 space-y-4">
          {connected.map((connection) => (
            <Link
              key={connection.id}
              to={routeSet.ATHLETE_DETAIL(connection.athlete_id)}
              className="group flex items-center justify-between rounded-4xl border border-border-default bg-surface-card p-6 shadow-sm transition hover:-translate-y-1 hover:border-brand-action-soft hover:shadow-xl hover:shadow-border-default/70"
            >
              <div>
                <h2 className="text-2xl font-bold text-text-primary">
                  {connection.athleteProfile?.full_name ?? "Athlete"}
                </h2>
                <p className="mt-2 text-sm text-text-muted">
                  {connection.athleteProfile?.email ?? ""}
                </p>
              </div>

              <ArrowRight className="h-5 w-5 shrink-0 text-text-disabled transition group-hover:translate-x-1 group-hover:text-brand-action" />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
