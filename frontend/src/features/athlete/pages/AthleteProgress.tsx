import { BarChart3, CalendarClock, Loader2, TrendingUp, Trophy } from "lucide-react";
import { Link } from "react-router-dom";

import EmptyState from "../../../components/shared/EmptyState";
import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { usePerformances } from "../../performances/hooks/usePerformances";
import { buildReadinessTrend, ReadinessTrendChart } from "../../performances/lib/readinessTrend";
import { useAthleteProfile } from "../hooks/useAthleteProfile";

// One entry per meaningful event in an athlete's journey. `score` is
// reserved, unused space for a future numeric Performance Index
// (roadmap step 8, not built) - once it exists, it slots into this same
// timeline row shape rather than requiring a rework of this page.
interface TimelineEntry {
  id: string;
  date: string;
  title: string;
  eventName: string;
  status: string | null;
  kind: "uploaded" | "completed" | "failed";
  score?: number;
}

function getEventName(events: unknown) {
  if (Array.isArray(events)) {
    return (events[0] as { name?: string } | undefined)?.name ?? "Performance";
  }
  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }
  return "Performance";
}

function formatDate(date?: string | null) {
  if (!date) return "Date unavailable";
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

function buildTimeline(performances: any[]): TimelineEntry[] {
  const entries: TimelineEntry[] = [];

  for (const performance of performances) {
    entries.push({
      id: `${performance.id}-uploaded`,
      date: performance.created_at,
      title: performance.title,
      eventName: getEventName(performance.events),
      status: performance.upload_status,
      kind: performance.upload_status === "failed" ? "failed" : "uploaded",
    });

    if (performance.upload_status === "completed") {
      entries.push({
        id: `${performance.id}-completed`,
        date: performance.updated_at ?? performance.created_at,
        title: performance.title,
        eventName: getEventName(performance.events),
        status: "completed",
        kind: "completed",
      });
    }
  }

  return entries.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

function dotClasses(kind: TimelineEntry["kind"]) {
  switch (kind) {
    case "completed":
      return "bg-green-600";
    case "failed":
      return "bg-red-500";
    default:
      return "bg-[#F0600E]";
  }
}

function labelFor(entry: TimelineEntry) {
  switch (entry.kind) {
    case "completed":
      return "Analysis completed";
    case "failed":
      return "Analysis failed";
    default:
      return "Performance uploaded";
  }
}

export default function AthleteProgress() {
  const { user } = useAuth();
  const { data: performances = [], isLoading, error } = usePerformances(user?.id);
  const { data: profileData } = useAthleteProfile(user?.id);

  const timeline = buildTimeline(performances);
  const readinessTrend = buildReadinessTrend(performances);
  const personalBest = profileData?.sporting?.personal_best;

  return (
    <div className="mx-auto max-w-4xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        Progress
      </p>
      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        Your Journey
      </h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        Every upload and completed analysis, in order. This is built entirely
        from your real performance history - no scores or trend lines are
        invented here.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-[#F0600E]" />
            <h2 className="font-bold text-gray-950">Personal Best</h2>
          </div>
          {personalBest ? (
            <p className="mt-4 text-2xl font-bold text-gray-950">{personalBest}</p>
          ) : (
            <p className="mt-4 text-sm text-gray-500">
              Not set yet -{" "}
              <Link to={ROUTES.ATHLETE.PROFILE} className="font-bold text-[#F0600E] hover:text-orange-700">
                add it to your profile
              </Link>
              .
            </p>
          )}
        </div>

        <div className="rounded-4xl border border-dashed border-gray-300 bg-gray-50 p-6">
          <div className="flex items-center gap-2 text-gray-400">
            <TrendingUp className="h-5 w-5" />
            <h2 className="text-sm font-bold uppercase tracking-widest">Score progression</h2>
          </div>
          <p className="mt-4 text-sm leading-6 text-gray-500">
            Reserved for a future Performance Index (roadmap step 8) - not
            built yet. Nothing is fabricated here in the meantime.
          </p>
        </div>
      </div>

      {!isLoading && !error && (
        <div className="mt-4 rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-[#F0600E]" />
            <h2 className="font-bold text-gray-950">Recording Readiness Trend</h2>
          </div>
          <p className="mt-2 text-sm leading-6 text-gray-500">
            Overall readiness score from each analyzed session, in order.
            Reflects recording quality, not an athletic performance score.
          </p>
          <ReadinessTrendChart points={readinessTrend} />
        </div>
      )}

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading your timeline...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-700">
          {error.message}
        </div>
      )}

      {!isLoading && !error && timeline.length === 0 && (
        <EmptyState
          icon={CalendarClock}
          title="Your timeline starts with your first upload"
          description="Upload a performance to begin building your journey."
        />
      )}

      {!isLoading && timeline.length > 0 && (
        <div className="mt-10 space-y-0">
          {timeline.map((entry, index) => (
            <div key={entry.id} className="relative flex gap-4 pb-8">
              {index < timeline.length - 1 && (
                <div className="absolute left-[7px] top-4 h-full w-px bg-gray-200" />
              )}
              <div className={`mt-1.5 h-4 w-4 shrink-0 rounded-full ${dotClasses(entry.kind)}`} />

              <div className="flex-1 rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
                <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.18em] text-[#F0600E]">
                  {labelFor(entry)}
                </p>
                <h3 className="mt-2 text-lg font-bold text-gray-950">{entry.title}</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {entry.eventName} · {formatDate(entry.date)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
