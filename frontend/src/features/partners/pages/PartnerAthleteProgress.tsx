import { ArrowLeft, Loader2 } from "lucide-react";
import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import {
  buildTwinPersonalBests,
  computeConsistency,
  computeTwinConfidence,
  deriveDevelopmentAreas,
  deriveDevelopmentStage,
  deriveStrengths,
  dominantEventName,
  generateEvolutionStatements,
  toTwinSessionInput,
  type TwinSessionInput,
} from "../../performances/lib/twinEngine";
import TwinSummary from "../../performances/components/twin/TwinSummary";
import TwinProgress from "../../performances/components/twin/TwinProgress";
import TwinStrengths from "../../performances/components/twin/TwinStrengths";
import TwinDevelopmentAreas from "../../performances/components/twin/TwinDevelopmentAreas";
import TwinConsistency from "../../performances/components/twin/TwinConsistency";
import TwinPersonalBests from "../../performances/components/twin/TwinPersonalBests";
import TwinEvolution from "../../performances/components/twin/TwinEvolution";
import { getAthleteProfile, getConnectedAthletePerformances } from "../services/connections.service";
import { usePartnerConnections } from "../hooks/usePartnerConnections";
import { getConnectionViewState } from "../lib/getConnectionViewState";

// The coach-side view of one connected athlete's Digital Twin - reuses
// every twinEngine.ts function and Twin* component as-is, the same way
// the athlete's own DigitalTwin.tsx does, rather than the bespoke
// readiness-trend-only rendering this page used before the Twin existed.
// This is the reusable-architecture payoff the Twin was explicitly built
// for (§25/§26 of docs/ENGINEERING_HANDOFF.md).
//
// Two sections are deliberately not reused here:
// - TwinAchievements/goals: athlete_goals RLS is owner-only (migration
//   0007, auth.uid() = athlete_id) - a coach query returns zero rows, so
//   this would render as a permanently, confusingly empty section.
// - TwinTimeline: PartnerAthleteDetail.tsx already lists this athlete's
//   full performance history - a second timeline here would be redundant.
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

  // Shares PartnerAthleteDetail.tsx's exact query key, so navigating
  // between the two pages doesn't refetch. BaseProfile (from
  // usePartnerConnections) has no personal_best field - that lives on
  // AthleteProfileSummary, fetched separately here same as there.
  const { data: athleteProfile } = useQuery({
    queryKey: ["partner-athlete-profile", athleteId],
    queryFn: async () => {
      const { data, error } = await getAthleteProfile(athleteId!);
      if (error) throw new Error(error.message);
      return data;
    },
    enabled: Boolean(isConnected && athleteId),
  });

  const twinSessions: TwinSessionInput[] = useMemo(
    () => performances.map(toTwinSessionInput),
    [performances],
  );

  const eventName = useMemo(() => dominantEventName(twinSessions), [twinSessions]);
  const developmentStage = useMemo(() => deriveDevelopmentStage(twinSessions), [twinSessions]);
  const confidence = useMemo(() => computeTwinConfidence(twinSessions), [twinSessions]);
  const consistency = useMemo(() => computeConsistency(twinSessions), [twinSessions]);
  const strengths = useMemo(() => deriveStrengths(twinSessions), [twinSessions]);
  const developmentAreas = useMemo(() => deriveDevelopmentAreas(twinSessions), [twinSessions]);
  const evolutionStatements = useMemo(
    () => generateEvolutionStatements(twinSessions),
    [twinSessions],
  );
  const personalBests = useMemo(() => buildTwinPersonalBests(twinSessions), [twinSessions]);

  const completedPerformances = useMemo(
    () => performances.filter((p: any) => p.upload_status === "completed"),
    [performances],
  );
  const latestAnalysisDate =
    completedPerformances.length > 0
      ? completedPerformances
          .map((p: any) => p.performance_date ?? p.created_at)
          .sort((a: string, b: string) => new Date(b).getTime() - new Date(a).getTime())[0]
      : null;

  // No coach-side single-performance route exists yet (PartnerAthleteDetail
  // shows the full history inline, §18.4) - link back to the athlete
  // detail page rather than a specific report. A disclosed v1
  // simplification, same spirit as PartnerCompare.tsx's "most recent
  // performance only" simplification.
  const personalBestItems = useMemo(
    () =>
      personalBests.map((pb) => ({
        ...pb,
        reportHref: routeSet.ATHLETE_DETAIL(athleteId!),
      })),
    [personalBests, routeSet, athleteId],
  );

  if (connectionsLoading) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-border-default bg-surface-card p-10 text-center shadow-sm">
        <Loader2 className="mx-auto h-9 w-9 animate-spin text-brand-action" />
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-error-failure bg-error-failure-soft p-10 text-center">
        <h1 className="text-2xl font-bold text-error-failure">You don't have access to this athlete.</h1>
        <Link
          to={routeSet.ATHLETES}
          className="mt-6 inline-flex rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white"
        >
          Back to {isAcademy ? "Squad" : "My Athletes"}
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl">
      <Link
        to={routeSet.ATHLETE_DETAIL(athleteId!)}
        className="inline-flex items-center gap-2 text-sm font-bold text-text-secondary transition hover:text-brand-action"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Athlete
      </Link>

      {performancesLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-border-default bg-surface-card p-6 text-sm font-semibold text-text-secondary shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-brand-action" />
          Loading sessions...
        </div>
      )}

      {!performancesLoading && (
        <div className="mt-8 space-y-14">
          <section>
            <TwinSummary
              athleteName={connection?.athleteProfile?.full_name ?? "Athlete"}
              eventName={eventName}
              developmentStageLabel={developmentStage.label}
              sessionCount={completedPerformances.length}
              latestAnalysisDate={latestAnalysisDate}
              personalBestLabel={(athleteProfile as any)?.personal_best ?? null}
              confidence={confidence}
            />
          </section>

          <section>
            <h2 className="mb-4 text-xl font-bold text-text-primary">Progress Engine</h2>
            <TwinProgress performances={twinSessions} />
          </section>

          <section>
            <h2 className="mb-4 text-xl font-bold text-text-primary">Strengths</h2>
            <TwinStrengths strengths={strengths} />
          </section>

          <section>
            <h2 className="mb-4 text-xl font-bold text-text-primary">Development Areas</h2>
            <TwinDevelopmentAreas areas={developmentAreas} />
          </section>

          <section>
            <h2 className="mb-4 text-xl font-bold text-text-primary">Consistency</h2>
            <TwinConsistency consistency={consistency} />
          </section>

          <section>
            <h2 className="mb-4 text-xl font-bold text-text-primary">Personal Bests</h2>
            <TwinPersonalBests items={personalBestItems} />
          </section>

          <section>
            <h2 className="mb-4 text-xl font-bold text-text-primary">Evolution</h2>
            <TwinEvolution statements={evolutionStatements} />
          </section>
        </div>
      )}
    </div>
  );
}
