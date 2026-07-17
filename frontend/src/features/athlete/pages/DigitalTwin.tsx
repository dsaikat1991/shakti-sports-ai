import { useMemo } from "react";
import { Loader2 } from "lucide-react";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { usePerformances } from "../../performances/hooks/usePerformances";
import { useAthleteProfile } from "../hooks/useAthleteProfile";
import { useAthleteGoals } from "../hooks/useAthleteGoals";
import { extractAnalysisSummary } from "../../performances/lib/analysisSummary";
import {
  type TwinSessionInput,
  buildTwinPersonalBests,
  computeConsistency,
  computeTwinConfidence,
  deriveDevelopmentAreas,
  deriveDevelopmentStage,
  deriveStrengths,
  dominantEventName,
  generateEvolutionStatements,
  toTwinSessionInput,
} from "../../performances/lib/twinEngine";
import TwinSummary from "../../performances/components/twin/TwinSummary";
import TwinTimeline from "../../performances/components/twin/TwinTimeline";
import TwinProgress from "../../performances/components/twin/TwinProgress";
import TwinStrengths from "../../performances/components/twin/TwinStrengths";
import TwinDevelopmentAreas from "../../performances/components/twin/TwinDevelopmentAreas";
import TwinConsistency from "../../performances/components/twin/TwinConsistency";
import TwinPersonalBests from "../../performances/components/twin/TwinPersonalBests";
import TwinEvolution from "../../performances/components/twin/TwinEvolution";
import TwinAchievements from "../../performances/components/twin/TwinAchievements";
import type { TwinSessionCardProps } from "../../performances/components/twin/TwinSessionCard";
import type { TwinPersonalBestItem } from "../../performances/components/twin/TwinPersonalBests";

const SECTION_NAV = [
  { id: "summary", label: "Summary" },
  { id: "timeline", label: "Timeline" },
  { id: "progress", label: "Progress" },
  { id: "strengths", label: "Strengths" },
  { id: "development", label: "Development" },
  { id: "consistency", label: "Consistency" },
  { id: "personal-bests", label: "Personal Bests" },
  { id: "evolution", label: "Evolution" },
  { id: "achievements", label: "Achievements" },
];

function getEventName(events: unknown): string {
  if (Array.isArray(events)) {
    return (events[0] as { name?: string } | undefined)?.name ?? "Performance";
  }
  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }
  return "Performance";
}

// The thin assembly layer - Step 2's Digital Twin Home. Every section
// below is a pure Twin* component; all computation lives in
// twinEngine.ts/analysisSummary.ts/metricRegistry.ts. This page's only
// job is fetching performances/profile/goals once and mapping them into
// the shapes each component expects.
export default function DigitalTwin() {
  const { user } = useAuth();
  const { data: performances = [], isLoading, error } = usePerformances(user?.id);
  const { data: profileData } = useAthleteProfile(user?.id);
  const { data: goals = [] } = useAthleteGoals(user?.id);

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
  const evolutionStatements = useMemo(() => generateEvolutionStatements(twinSessions), [twinSessions]);
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

  const timelineSessions: TwinSessionCardProps[] = useMemo(
    () =>
      [...performances]
        .sort(
          (a: any, b: any) =>
            new Date(b.performance_date ?? b.created_at).getTime() -
            new Date(a.performance_date ?? a.created_at).getTime(),
        )
        .map((p: any) => ({
          performanceNumber: p.performance_number ?? 0,
          title: p.title,
          date: p.performance_date ?? p.created_at,
          eventName: getEventName(p.events),
          status: p.upload_status,
          summary: extractAnalysisSummary(p.analysis_result),
          notes: p.notes ?? null,
          reportHref: ROUTES.ATHLETE.PERFORMANCE_REPORT(p.id),
        })),
    [performances],
  );

  const personalBestItems: TwinPersonalBestItem[] = useMemo(
    () =>
      personalBests.map((pb) => ({
        ...pb,
        reportHref: ROUTES.ATHLETE.PERFORMANCE_REPORT(pb.performanceId),
      })),
    [personalBests],
  );

  const completedGoals = useMemo(
    () =>
      (goals as any[])
        .filter((g) => g.status === "completed")
        .map((g) => ({ description: g.description, updatedAt: g.updated_at })),
    [goals],
  );

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-gray-200 bg-white p-10 text-center shadow-sm">
        <Loader2 className="mx-auto h-9 w-9 animate-spin text-[#F0600E]" />
        <p className="mt-4 text-sm font-bold text-gray-600">Loading your Digital Twin...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-red-200 bg-red-50 p-10 text-center">
        <p className="text-sm font-bold text-red-700">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-14">
      <nav className="sticky top-16 z-30 -mx-6 overflow-x-auto border-b border-gray-200 bg-[#FAFAF7]/95 px-6 py-3 backdrop-blur lg:mx-0 lg:rounded-2xl lg:border lg:px-4">
        <div className="flex gap-1 whitespace-nowrap">
          {SECTION_NAV.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className="rounded-xl px-3 py-1.5 text-xs font-bold uppercase tracking-wide text-gray-500 transition hover:bg-orange-50 hover:text-[#F0600E]"
            >
              {item.label}
            </a>
          ))}
        </div>
      </nav>

      <section id="summary" className="scroll-mt-32">
        <TwinSummary
          athleteName={profileData?.base?.full_name ?? user?.email ?? "Athlete"}
          eventName={eventName}
          developmentStageLabel={developmentStage.label}
          sessionCount={completedPerformances.length}
          latestAnalysisDate={latestAnalysisDate}
          personalBestLabel={profileData?.sporting?.personal_best ?? null}
          confidence={confidence}
        />
      </section>

      <section id="timeline" className="scroll-mt-32">
        <h2 className="mb-4 font-['Anton'] text-3xl uppercase text-gray-950">Timeline</h2>
        <TwinTimeline sessions={timelineSessions} />
      </section>

      <section id="progress" className="scroll-mt-32">
        <h2 className="mb-4 font-['Anton'] text-3xl uppercase text-gray-950">Progress Engine</h2>
        <TwinProgress performances={twinSessions} />
      </section>

      <section id="strengths" className="scroll-mt-32">
        <h2 className="mb-4 font-['Anton'] text-3xl uppercase text-gray-950">Strengths</h2>
        <TwinStrengths strengths={strengths} />
      </section>

      <section id="development" className="scroll-mt-32">
        <h2 className="mb-4 font-['Anton'] text-3xl uppercase text-gray-950">Development Areas</h2>
        <TwinDevelopmentAreas areas={developmentAreas} />
      </section>

      <section id="consistency" className="scroll-mt-32">
        <h2 className="mb-4 font-['Anton'] text-3xl uppercase text-gray-950">Consistency</h2>
        <TwinConsistency consistency={consistency} />
      </section>

      <section id="personal-bests" className="scroll-mt-32">
        <h2 className="mb-4 font-['Anton'] text-3xl uppercase text-gray-950">Personal Bests</h2>
        <TwinPersonalBests items={personalBestItems} />
      </section>

      <section id="evolution" className="scroll-mt-32">
        <h2 className="mb-4 font-['Anton'] text-3xl uppercase text-gray-950">Evolution</h2>
        <TwinEvolution statements={evolutionStatements} />
      </section>

      <section id="achievements" className="scroll-mt-32">
        <h2 className="mb-4 font-['Anton'] text-3xl uppercase text-gray-950">Achievements</h2>
        <TwinAchievements
          achievementsText={profileData?.sporting?.achievements ?? null}
          completedGoals={completedGoals}
        />
      </section>
    </div>
  );
}
