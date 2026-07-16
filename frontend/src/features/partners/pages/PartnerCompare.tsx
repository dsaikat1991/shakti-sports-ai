import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, GitCompare, Loader2 } from "lucide-react";
import { useMemo, useState } from "react";

import { RatingBadge } from "../../performances/pages/PerformanceDetail";
import type { AnalysisResult } from "../../performances/types/analysis";
import {
  METRIC_REGISTRY,
  checkMetricComparability,
  checkPairComparability,
  getEventName,
} from "../../performances/lib/metricRegistry";
import { getConnectedAthletePerformances } from "../services/connections.service";
import { useAuth } from "../../auth/context/AuthContext";
import { usePartnerConnections } from "../hooks/usePartnerConnections";
import { getConnectionViewState } from "../lib/getConnectionViewState";

// Picks the most recent COMPLETED performance with a real analysis
// result - never fabricates a comparison from a still-processing or
// failed upload. "Most recent" is a v1 simplification (no per-
// performance picker yet) - documented, not hidden.
function latestCompletedPerformance(performances: any[]) {
  const completed = performances.filter(
    (p) => p.upload_status === "completed" && p.analysis_result,
  );
  if (completed.length === 0) return null;

  return [...completed].sort(
    (a, b) =>
      new Date(b.performance_date ?? b.created_at).getTime() -
      new Date(a.performance_date ?? a.created_at).getTime(),
  )[0];
}

function useAthletePerformances(athleteId: string | null) {
  return useQuery({
    queryKey: ["coach-athlete-performances", athleteId],
    queryFn: async () => {
      if (!athleteId) return [];
      const { data, error } = await getConnectedAthletePerformances(athleteId);
      if (error) throw new Error(error.message);
      return data ?? [];
    },
    enabled: Boolean(athleteId),
  });
}

function AthletePicker({
  label,
  athletes,
  value,
  onChange,
  exclude,
}: {
  label: string;
  athletes: { athlete_id: string; name: string }[];
  value: string;
  onChange: (id: string) => void;
  exclude?: string;
}) {
  return (
    <div className="flex-1">
      <p className="mb-2 text-xs font-bold uppercase tracking-widest text-gray-400">{label}</p>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm outline-none focus:border-[#F0600E]"
      >
        <option value="">Choose an athlete...</option>
        {athletes
          .filter((a) => a.athlete_id !== exclude)
          .map((a) => (
            <option key={a.athlete_id} value={a.athlete_id}>
              {a.name}
            </option>
          ))}
      </select>
    </div>
  );
}

export default function PartnerCompare() {
  const { user } = useAuth();
  const { data: connections = [] } = usePartnerConnections(user?.id);

  const connectedAthletes = user
    ? connections
        .filter((c) => getConnectionViewState(c, user.id) === "connected")
        .map((c) => ({ athlete_id: c.athlete_id, name: c.athleteProfile?.full_name ?? "Athlete" }))
    : [];

  const [athleteAId, setAthleteAId] = useState("");
  const [athleteBId, setAthleteBId] = useState("");

  const performancesA = useAthletePerformances(athleteAId || null);
  const performancesB = useAthletePerformances(athleteBId || null);

  const performanceA = useMemo(
    () => latestCompletedPerformance(performancesA.data ?? []),
    [performancesA.data],
  );
  const performanceB = useMemo(
    () => latestCompletedPerformance(performancesB.data ?? []),
    [performancesB.data],
  );

  const bothSelected = Boolean(athleteAId && athleteBId);
  const loading = performancesA.isLoading || performancesB.isLoading;

  const nameA = connectedAthletes.find((a) => a.athlete_id === athleteAId)?.name ?? "Athlete A";
  const nameB = connectedAthletes.find((a) => a.athlete_id === athleteBId)?.name ?? "Athlete B";

  const pairComparability = useMemo(() => {
    if (!performanceA || !performanceB) return null;
    return checkPairComparability(
      getEventName(performanceA.events),
      getEventName(performanceB.events),
      performanceA.analysis_result as AnalysisResult,
      performanceB.analysis_result as AnalysisResult,
    );
  }, [performanceA, performanceB]);

  return (
    <div className="mx-auto max-w-5xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        Compare
      </p>
      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        Athlete Comparison
      </h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        Side-by-side comparison of two connected athletes' most recent
        completed reports. Only real, completed analyses are used - nothing
        here is estimated or invented.
      </p>

      <div className="mt-8 flex flex-col gap-4 rounded-3xl border border-gray-200 bg-white p-5 shadow-sm sm:flex-row">
        <AthletePicker
          label="Athlete A"
          athletes={connectedAthletes}
          value={athleteAId}
          onChange={setAthleteAId}
          exclude={athleteBId}
        />
        <AthletePicker
          label="Athlete B"
          athletes={connectedAthletes}
          value={athleteBId}
          onChange={setAthleteBId}
          exclude={athleteAId}
        />
      </div>

      {connectedAthletes.length < 2 && (
        <div className="mt-10 rounded-4xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center">
          <GitCompare className="mx-auto h-11 w-11 text-gray-400" />
          <h2 className="mt-5 text-2xl font-bold text-gray-950">Need two connected athletes</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
            Comparison only works between athletes you're currently connected
            to - connect with at least one more athlete to use this.
          </p>
        </div>
      )}

      {bothSelected && loading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading reports...
        </div>
      )}

      {bothSelected && !loading && (!performanceA || !performanceB) && (
        <div className="mt-10 rounded-4xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center">
          <AlertTriangle className="mx-auto h-9 w-9 text-gray-400" />
          <h2 className="mt-4 text-xl font-bold text-gray-950">
            {!performanceA && !performanceB
              ? "Neither athlete has a completed report yet"
              : !performanceA
                ? `${nameA} doesn't have a completed report yet`
                : `${nameB} doesn't have a completed report yet`}
          </h2>
        </div>
      )}

      {bothSelected && !loading && performanceA && performanceB && pairComparability && (
        <div className="mt-8">
          {!pairComparability.comparable ? (
            <div className="rounded-3xl border border-amber-200 bg-amber-50 p-6">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-700" />
                <p className="text-sm font-bold text-amber-900">Not Comparable</p>
              </div>
              <p className="mt-2 text-sm leading-6 text-amber-800">{pairComparability.reason}</p>
            </div>
          ) : (
            <ComparisonTable
              nameA={nameA}
              nameB={nameB}
              resultA={performanceA.analysis_result as AnalysisResult}
              resultB={performanceB.analysis_result as AnalysisResult}
              eventName={getEventName(performanceA.events)}
            />
          )}
        </div>
      )}
    </div>
  );
}

function ComparisonTable({
  nameA,
  nameB,
  resultA,
  resultB,
  eventName,
}: {
  nameA: string;
  nameB: string;
  resultA: AnalysisResult;
  resultB: AnalysisResult;
  eventName: string;
}) {
  const qualityA = resultA.recording_quality as any;
  const qualityB = resultB.recording_quality as any;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-3xl border border-gray-200 bg-white p-5 text-center shadow-sm">
          <h2 className="text-lg font-bold text-gray-950">{nameA}</h2>
          <div className="mt-2">
            <RatingBadge rating={qualityA?.rating} />
          </div>
        </div>
        <div className="rounded-3xl border border-gray-200 bg-white p-5 text-center shadow-sm">
          <h2 className="text-lg font-bold text-gray-950">{nameB}</h2>
          <div className="mt-2">
            <RatingBadge rating={qualityB?.rating} />
          </div>
        </div>
      </div>

      <MetricSection
        title="Recording Quality"
        metrics={METRIC_REGISTRY.filter((m) => m.category === "recording_quality")}
        resultA={resultA}
        resultB={resultB}
        eventName={eventName}
      />

      <MetricSection
        title="Biomechanics"
        metrics={METRIC_REGISTRY.filter((m) => m.category === "biomechanics" && m.status === "production")}
        resultA={resultA}
        resultB={resultB}
        eventName={eventName}
      />

      <div>
        <h3 className="mb-3 text-xs font-bold uppercase tracking-widest text-amber-700">
          Experimental Metrics
        </h3>
        <p className="mb-3 text-sm leading-6 text-gray-500">
          Ground-contact detection is confirmed unreliable for some camera
          angles (see the Limitations section of each full report) - these
          are shown for reference only and never used to suggest a winner.
        </p>
        <MetricSection
          title=""
          metrics={METRIC_REGISTRY.filter((m) => m.category === "biomechanics" && m.status === "experimental")}
          resultA={resultA}
          resultB={resultB}
          eventName={eventName}
          experimental
        />
      </div>
    </div>
  );
}

function MetricSection({
  title,
  metrics,
  resultA,
  resultB,
  eventName,
  experimental,
}: {
  title: string;
  metrics: typeof METRIC_REGISTRY;
  resultA: AnalysisResult;
  resultB: AnalysisResult;
  eventName: string;
  experimental?: boolean;
}) {
  if (metrics.length === 0) return null;

  return (
    <div className={`rounded-3xl border p-5 ${experimental ? "border-amber-200 bg-amber-50/40" : "border-gray-200 bg-white shadow-sm"}`}>
      {title && <h3 className="mb-3 text-xs font-bold uppercase tracking-widest text-gray-400">{title}</h3>}

      <div className="space-y-3">
        {metrics.map((metric) => {
          const a = metric.accessor(resultA);
          const b = metric.accessor(resultB);
          const comparability = checkMetricComparability(metric, eventName, a, b);

          let winner: "a" | "b" | null = null;
          if (comparability.comparable && a && b && !experimental) {
            if (a.value !== b.value) winner = a.value > b.value ? "a" : "b";
          }

          return (
            <div key={metric.key} className="grid grid-cols-3 items-center gap-3 border-t border-gray-100 pt-3 first:border-t-0 first:pt-0">
              <p className="text-sm font-semibold text-gray-700">{metric.label}</p>

              {comparability.comparable ? (
                <>
                  <p className={`text-sm font-bold ${winner === "a" ? "text-green-700" : "text-gray-950"}`}>
                    {a ? metric.format(a) : "N/A"}
                  </p>
                  <p className={`text-sm font-bold ${winner === "b" ? "text-green-700" : "text-gray-950"}`}>
                    {b ? metric.format(b) : "N/A"}
                  </p>
                </>
              ) : (
                <p className="col-span-2 text-xs font-semibold text-gray-400">
                  Not comparable - {comparability.reason}
                </p>
              )}
            </div>
          );
        })}
      </div>

      {metrics[0]?.limitationText && (
        <p className="mt-4 text-xs leading-5 text-amber-700">{metrics[0].limitationText}</p>
      )}
    </div>
  );
}
