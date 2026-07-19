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
import type { ComparisonMode } from "../../performances/lib/metricRegistry";
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
      <p className="mb-2 text-xs font-bold uppercase tracking-widest text-text-disabled">{label}</p>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-xl border border-border-default px-3 py-2.5 text-sm outline-none focus:border-brand-action"
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
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
        Compare
      </p>
      <h1 className="mt-3 text-2xl font-bold text-text-primary md:text-3xl">
        Athlete Comparison
      </h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-text-secondary">
        Side-by-side comparison of two connected athletes' most recent
        completed reports. Only real, completed analyses are used - nothing
        here is estimated or invented.
      </p>

      <div className="mt-8 flex flex-col gap-4 rounded-3xl border border-border-default bg-surface-card p-5 shadow-sm sm:flex-row">
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
        <div className="mt-10 rounded-4xl border border-dashed border-border-default bg-surface-sunken p-10 text-center">
          <GitCompare className="mx-auto h-11 w-11 text-text-disabled" />
          <h2 className="mt-5 text-2xl font-bold text-text-primary">Need two connected athletes</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-text-muted">
            Comparison only works between athletes you're currently connected
            to - connect with at least one more athlete to use this.
          </p>
        </div>
      )}

      {bothSelected && loading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-border-default bg-surface-card p-6 text-sm font-semibold text-text-secondary shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-brand-action" />
          Loading reports...
        </div>
      )}

      {bothSelected && !loading && (!performanceA || !performanceB) && (
        <div className="mt-10 rounded-4xl border border-dashed border-border-default bg-surface-sunken p-10 text-center">
          <AlertTriangle className="mx-auto h-9 w-9 text-text-disabled" />
          <h2 className="mt-4 text-xl font-bold text-text-primary">
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
            <div className="rounded-3xl border border-warning-attention bg-warning-attention-soft p-6">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning-attention" />
                <p className="text-sm font-bold text-warning-attention">Not Comparable</p>
              </div>
              <p className="mt-2 text-sm leading-6 text-warning-attention">{pairComparability.reason}</p>
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
        <div className="rounded-3xl border border-border-default bg-surface-card p-5 text-center shadow-sm">
          <h2 className="text-lg font-bold text-text-primary">{nameA}</h2>
          <div className="mt-2">
            <RatingBadge rating={qualityA?.rating} />
          </div>
        </div>
        <div className="rounded-3xl border border-border-default bg-surface-card p-5 text-center shadow-sm">
          <h2 className="text-lg font-bold text-text-primary">{nameB}</h2>
          <div className="mt-2">
            <RatingBadge rating={qualityB?.rating} />
          </div>
        </div>
      </div>

      <MetricSection
        title="Recording Quality"
        metrics={METRIC_REGISTRY.filter(
          (m) => m.category === "recording_quality" && m.status === "production" && m.supportsCoachComparison && !m.hidden,
        )}
        resultA={resultA}
        resultB={resultB}
        eventName={eventName}
      />

      <MetricSection
        title="Biomechanics"
        metrics={METRIC_REGISTRY.filter(
          (m) => m.category === "biomechanics" && m.status === "production" && m.supportsCoachComparison && !m.hidden,
        )}
        resultA={resultA}
        resultB={resultB}
        eventName={eventName}
      />

      <div>
        <h3 className="mb-3 text-xs font-bold uppercase tracking-widest text-warning-attention">
          Experimental Metrics
        </h3>
        <p className="mb-3 text-sm leading-6 text-text-muted">
          Ground-contact detection is confirmed unreliable for some camera
          angles (see the Limitations section of each full report) - these
          are shown for reference only and never used to suggest a winner.
        </p>
        <MetricSection
          title=""
          metrics={METRIC_REGISTRY.filter(
            (m) => m.category === "biomechanics" && m.status === "experimental" && m.supportsCoachComparison && !m.hidden,
          )}
          resultA={resultA}
          resultB={resultB}
          eventName={eventName}
          experimental
        />
      </div>
    </div>
  );
}

// The single place a "winner" is decided between two values of the same
// metric - derived entirely from comparisonMode, never from the raw
// number alone (docs/ENGINEERING_HANDOFF.md §33). TARGET_RANGE has no
// winner today because no metric in the registry actually uses it (no
// validated target range has ever been defined in this codebase) - if
// one is added later with a real range, this function is the one place
// that would need a new case, not every call site that renders a
// comparison.
function winningSide(comparisonMode: ComparisonMode, valueA: number, valueB: number): "a" | "b" | null {
  if (valueA === valueB) return null;

  switch (comparisonMode) {
    case "HIGHER_IS_BETTER":
      return valueA > valueB ? "a" : "b";
    case "LOWER_IS_BETTER":
      return valueA < valueB ? "a" : "b";
    case "SYMMETRY":
      // knee_symmetry_score (the only current SYMMETRY metric) already
      // encodes "closer to symmetric" as a higher score - so higher wins,
      // same arithmetic as HIGHER_IS_BETTER but kept as its own case since
      // a future symmetry-style metric might not share that encoding.
      return valueA > valueB ? "a" : "b";
    case "NEUTRAL":
    case "EXPERIMENTAL":
    case "TARGET_RANGE":
    case "NOT_COMPARABLE":
      return null;
  }
}

export function MetricSection({
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
  // Visual treatment only (the amber tint below) - winner suppression for
  // experimental metrics comes from comparisonMode ("EXPERIMENTAL" always
  // yields no winner, enforced by the registry itself), not from this
  // prop. Kept because the section header/styling still needs to know.
  experimental?: boolean;
}) {
  if (metrics.length === 0) return null;

  return (
    <div className={`rounded-3xl border p-5 ${experimental ? "border-warning-attention bg-warning-attention-tint" : "border-border-default bg-surface-card shadow-sm"}`}>
      {title && <h3 className="mb-3 text-xs font-bold uppercase tracking-widest text-text-disabled">{title}</h3>}

      <div className="space-y-3">
        {metrics.map((metric) => {
          const a = metric.accessor(resultA);
          const b = metric.accessor(resultB);
          const comparability = checkMetricComparability(metric, eventName, a, b);

          const winner: "a" | "b" | null =
            comparability.comparable && a && b ? winningSide(metric.comparisonMode, a.value, b.value) : null;

          return (
            <div key={metric.key} className="grid grid-cols-3 items-center gap-3 border-t border-border-divider pt-3 first:border-t-0 first:pt-0">
              <p className="text-sm font-semibold text-text-secondary">{metric.label}</p>

              {comparability.comparable ? (
                <>
                  <p className={`text-sm font-bold ${winner === "a" ? "text-success-progress" : "text-text-primary"}`}>
                    {a ? metric.format(a) : "N/A"}
                  </p>
                  <p className={`text-sm font-bold ${winner === "b" ? "text-success-progress" : "text-text-primary"}`}>
                    {b ? metric.format(b) : "N/A"}
                  </p>
                </>
              ) : (
                <p className="col-span-2 text-xs font-semibold text-text-disabled">
                  Not comparable - {comparability.reason}
                </p>
              )}
            </div>
          );
        })}
      </div>

      {metrics[0]?.limitationText && (
        <p className="mt-4 text-xs leading-5 text-warning-attention">{metrics[0].limitationText}</p>
      )}
    </div>
  );
}
