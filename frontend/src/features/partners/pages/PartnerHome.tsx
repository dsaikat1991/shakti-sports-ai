import { ArrowRight, Inbox, Loader2, Users } from "lucide-react";
import { Link } from "react-router-dom";

import EmptyState from "../../../components/shared/EmptyState";
import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { usePartnerConnections } from "../hooks/usePartnerConnections";
import { getConnectionViewState } from "../lib/getConnectionViewState";

export default function PartnerHome() {
  const { user, role } = useAuth();
  const isAcademy = role === "academy";
  const routeSet = isAcademy ? ROUTES.ACADEMY : ROUTES.COACH;

  const { data: connections = [], isLoading, error } = usePartnerConnections(user?.id);

  const connected = user
    ? connections.filter((c) => getConnectionViewState(c, user.id) === "connected")
    : [];
  const incoming = user
    ? connections.filter((c) => getConnectionViewState(c, user.id) === "incoming_request")
    : [];

  return (
    <div className="mx-auto max-w-6xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
        {isAcademy ? "Academy Console" : "Coach Console"}
      </p>

      <h1 className="mt-3 text-2xl font-bold text-text-primary md:text-3xl">
        {isAcademy ? "Your Squad" : "Your Athletes"}
      </h1>

      <p className="mt-4 max-w-2xl text-base leading-7 text-text-secondary">
        Connect with athletes to review their performance history and
        Shakti Motion Intelligence™ reports.
      </p>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-border-default bg-surface-card p-6 text-sm font-semibold text-text-secondary shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-brand-action" />
          Loading your connections...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-error-failure bg-error-failure-soft p-6 text-sm font-semibold text-error-failure">
          {error.message}
        </div>
      )}

      {!isLoading && !error && (
        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          <Link
            to={routeSet.ATHLETES}
            className="group rounded-4xl border border-border-default bg-surface-card p-6 shadow-sm transition hover:-translate-y-1 hover:border-brand-action-soft hover:shadow-xl hover:shadow-border-default/70"
          >
            <div className="flex items-center justify-between">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-action-soft text-brand-action">
                <Users className="h-6 w-6" />
              </div>
              <ArrowRight className="h-5 w-5 text-text-disabled transition group-hover:translate-x-1 group-hover:text-brand-action" />
            </div>

            <p className="mt-5 text-4xl font-black text-text-primary">{connected.length}</p>
            <p className="mt-1 text-sm font-semibold text-text-secondary">
              {isAcademy ? "Athletes in your squad" : "Connected athletes"}
            </p>
          </Link>

          <Link
            to={routeSet.REQUESTS}
            className="group rounded-4xl border border-border-default bg-surface-card p-6 shadow-sm transition hover:-translate-y-1 hover:border-brand-action-soft hover:shadow-xl hover:shadow-border-default/70"
          >
            <div className="flex items-center justify-between">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-action-soft text-brand-action">
                <Inbox className="h-6 w-6" />
              </div>
              <ArrowRight className="h-5 w-5 text-text-disabled transition group-hover:translate-x-1 group-hover:text-brand-action" />
            </div>

            <p className="mt-5 text-4xl font-black text-text-primary">{incoming.length}</p>
            <p className="mt-1 text-sm font-semibold text-text-secondary">
              Pending requests to review
            </p>
          </Link>
        </div>
      )}

      {!isLoading && !error && connected.length === 0 && incoming.length === 0 && (
        <EmptyState
          icon={Users}
          title="No connections yet"
          description="Invite an athlete by email from the Requests page to start reviewing their performances."
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
    </div>
  );
}
