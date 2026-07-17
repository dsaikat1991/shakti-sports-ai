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
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        {isAcademy ? "Academy Console" : "Coach Console"}
      </p>

      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        {isAcademy ? "Your Squad" : "Your Athletes"}
      </h1>

      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        Connect with athletes to review their performance history and
        Shakti Motion Intelligence™ reports.
      </p>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading your connections...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-700">
          {error.message}
        </div>
      )}

      {!isLoading && !error && (
        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          <Link
            to={routeSet.ATHLETES}
            className="group rounded-4xl border border-gray-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-orange-200 hover:shadow-xl hover:shadow-gray-200/70"
          >
            <div className="flex items-center justify-between">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-orange-100 text-[#F0600E]">
                <Users className="h-6 w-6" />
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400 transition group-hover:translate-x-1 group-hover:text-[#F0600E]" />
            </div>

            <p className="mt-5 text-4xl font-black text-gray-950">{connected.length}</p>
            <p className="mt-1 text-sm font-semibold text-gray-600">
              {isAcademy ? "Athletes in your squad" : "Connected athletes"}
            </p>
          </Link>

          <Link
            to={routeSet.REQUESTS}
            className="group rounded-4xl border border-gray-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-orange-200 hover:shadow-xl hover:shadow-gray-200/70"
          >
            <div className="flex items-center justify-between">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-orange-100 text-[#F0600E]">
                <Inbox className="h-6 w-6" />
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400 transition group-hover:translate-x-1 group-hover:text-[#F0600E]" />
            </div>

            <p className="mt-5 text-4xl font-black text-gray-950">{incoming.length}</p>
            <p className="mt-1 text-sm font-semibold text-gray-600">
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
              className="mt-6 inline-flex items-center justify-center gap-2 rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
            >
              Invite an Athlete
            </Link>
          }
        />
      )}
    </div>
  );
}
