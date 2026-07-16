import { ArrowLeft, BarChart3, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import {
  METRIC_REGISTRY,
  getEventName,
} from "../../performances/lib/metricRegistry";
import {
  ReadinessTrendChart,
  buildMetricTrend,
  buildReadinessTrend,
  MetricTrendChart,
} from "../../performances/lib/readinessTrend";
import { getConnectedAthletePerformances } from "../services/connections.service";
import { usePartnerConnections } from "../hooks/usePartnerConnections";
import { getConnectionViewState } from "../lib/getConnectionViewState";

// One connected athlete's sessions over time, from the coach's side -
// reuses the exact same trend-building logic as the athlete's own
// Progress page (features/performances/lib/readinessTrend.tsx), not a
// re-implementation. Adds production-status biomechanics metric trends
// (cadence, knee symmetry) on top of the recording-readiness trend,
// since a coach cares more about those than an athlete reviewing their
// own recording quality does - experimental metrics (ground contacts,
// duty factor, flight time) are deliberately left off a trend view,
// where a rising/falling line would read as a real signal even though
// §10.1 already proved this detector cannot be trusted.
const PROGRESS_METRIC_KEYS = ["cadence", "knee_symmetry"];

export default function PartnerAthleteProgress() {
  const { athleteId } = useParams();
  const { user, role } = useAuth();
  const isAcademy = role === "academy";
  const routeSet = isAcademy ? ROUTES.ACADEMY : ROUTES.COACH;

  const { data: connections = [], isLoading: connectionsLoading } = usePartnerConnections(user?.id);
  const connection = connections.find((c) => c.athlete_id === athleteId);
  const isConnected =
    connection && user && getConnectionViewState(connection, user.id) === "connected";

  const { data: performances = [], isLoading: performancesLoading } = useQuery({
    queryKey: ["coach-athlete-performances", athleteId],
    queryFn: async () => {
      const { data, error } = await getConnectedAthletePerformances(athleteId!);
      if (error) throw new Error(error.message);
      return data ?? [];
    },
    enabled: Boolean(isConnected && athleteId),
  });

  if (connectionsLoading) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-gray-200 bg-white p-10 text-center shadow-sm">
        <Loader2 className="mx-auto h-9 w-9 animate-spin text-[#F0600E]" />
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-red-200 bg-red-50 p-10 text-center">
        <h1 className="text-2xl font-bold text-red-700">You don't have access to this athlete.</h1>
        <Link
          to={routeSet.ATHLETES}
          className="mt-6 inline-flex rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white"
        >
          Back to {isAcademy ? "Squad" : "My Athletes"}
        </Link>
      </div>
    );
  }

  const readinessTrend = buildReadinessTrend(performances);

  const completedEventNames = new Set(
    performances
      .filter((p: any) => p.upload_status === "completed")
      .map((p: any) => getEventName(p.events)),
  );

  return (
    <div className="mx-auto max-w-4xl">
      <Link
        to={routeSet.ATHLETE_DETAIL(athleteId!)}
        className="inline-flex items-center gap-2 text-sm font-bold text-gray-600 transition hover:text-[#F0600E]"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Athlete
      </Link>

      <p className="mt-6 font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        Progress Over Time
      </p>
      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        {connection?.athleteProfile?.full_name ?? "Athlete"}
      </h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        Built entirely from this athlete's real completed sessions - no
        scores or trend lines are invented where data doesn't exist yet.
      </p>

      {performancesLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading sessions...
        </div>
      )}

      {!performancesLoading && (
        <div className="mt-8 space-y-4">
          <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-[#F0600E]" />
              <h2 className="font-bold text-gray-950">Recording Readiness Trend</h2>
            </div>
            <p className="mt-2 text-sm leading-6 text-gray-500">
              Reflects recording quality, not an athletic performance score -
              see the biomechanics metrics below for that.
            </p>
            <ReadinessTrendChart points={readinessTrend} />
          </div>

          {METRIC_REGISTRY.filter(
            (m) => PROGRESS_METRIC_KEYS.includes(m.key) && m.status === "production",
          ).map((metric) => {
            const applicable = metric.applicableEvents.some((e) => completedEventNames.has(e));
            if (!applicable) return null;

            const points = buildMetricTrend(performances, metric);

            return (
              <div key={metric.key} className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
                <h2 className="font-bold text-gray-950">{metric.label} Trend</h2>
                <p className="mt-2 text-sm leading-6 text-gray-500">
                  {metric.unit ? `Measured in ${metric.unit}.` : ""} Only completed sessions with
                  this metric available are shown.
                </p>
                <MetricTrendChart points={points} format={(v) => metric.format({ value: v })} />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
