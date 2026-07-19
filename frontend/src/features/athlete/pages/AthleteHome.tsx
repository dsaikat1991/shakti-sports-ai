import { useMemo } from "react";
import {
  ArrowRight,
  Bell,
  CalendarDays,
  Loader2,
  Plus,
  RefreshCw,
  ShieldAlert,
  Target,
  Users,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { friendlyErrorMessage } from "../../../lib/friendlyError";
import { useAuth } from "../../auth/context/AuthContext";
import { useAthleteDashboard } from "../hooks/useAthleteDashboard";
import { useAthleteProfile } from "../hooks/useAthleteProfile";
import { useAthleteGoals } from "../hooks/useAthleteGoals";
import { useAthleteNotifications } from "../hooks/useAthleteNotifications";
import type { NotificationType } from "../lib/deriveNotifications";
import {
  extractAnalysisSummary,
  formatSessionDate,
} from "../../performances/lib/analysisSummary";
import { buildPerformanceDisplayName } from "../../performances/lib/performanceDisplayName";
import { buildReportHeadline } from "../../performances/lib/reportHeadline";
import { METRIC_REGISTRY } from "../../performances/lib/metricRegistry";
import {
  computeTwinConfidence,
  toTwinSessionInput,
  type ConfidenceLevel,
} from "../../performances/lib/twinEngine";
import { useRetryAnalysis } from "../../performances/hooks/useRetryAnalysis";
import { RatingBadge } from "../../performances/pages/PerformanceDetail";

const CADENCE_METRIC = METRIC_REGISTRY.find((m) => m.key === "cadence")!;
const STRIDE_FREQUENCY_METRIC = METRIC_REGISTRY.find((m) => m.key === "stride_frequency")!;
const DUTY_FACTOR_METRIC = METRIC_REGISTRY.find((m) => m.key === "duty_factor")!;

const CONFIDENCE_LABEL: Record<ConfidenceLevel, string> = {
  low: "Just getting started",
  medium: "Building",
  high: "Well established",
};

const CONFIDENCE_STEP_COUNT: Record<ConfidenceLevel, number> = {
  low: 1,
  medium: 2,
  high: 3,
};

function getGreeting() {
  const hour = new Date().getHours();

  if (hour >= 5 && hour < 12) return "Good morning";
  if (hour >= 12 && hour < 17) return "Good afternoon";
  if (hour >= 17 && hour < 21) return "Good evening";

  return "Good night";
}

function getEventName(events: unknown) {
  if (Array.isArray(events)) {
    const firstEvent = events[0] as { name?: string } | undefined;
    return firstEvent?.name ?? "Performance";
  }

  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }

  return "Performance";
}

function formatTargetDate(date?: string | null) {
  if (!date) return null;
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

function notificationIcon(type: NotificationType) {
  switch (type) {
    case "recording_quality_insufficient":
      return ShieldAlert;
    case "coach_connection_request":
      return Users;
    case "goal_target_date":
      return Target;
    default:
      return Bell;
  }
}

function getStatusLabel(status: string | null) {
  switch (status) {
    case "completed":
      return "Completed";
    case "processing":
      return "Processing";
    case "analyzing":
      return "Analyzing";
    case "failed":
      return "Failed";
    default:
      return "Uploaded";
  }
}

// Colors follow the project's official semantic token system: green =
// achievement (a completed job is a real pass), blue = informational (a
// job that's still in progress is neutral information, not a judgment),
// red = a genuine failure, brand-orange-soft = the default "just
// uploaded, nothing to report yet" neutral state.
function getStatusClasses(status: string | null) {
  switch (status) {
    case "completed":
      return "bg-success-progress-soft text-success-progress";
    case "processing":
    case "analyzing":
      return "bg-info-insight-soft text-info-insight";
    case "failed":
      return "bg-error-failure-soft text-error-failure";
    default:
      return "bg-brand-action-soft text-brand-action";
  }
}

// One explicit state machine for the hero, matching the same pattern
// PerformanceProcessing.tsx already uses - every real upload_status /
// biomechanics-readiness combination the latest performance can actually
// be in has exactly one representation here, not scattered booleans.
export type HomeHeroState =
  | { kind: "first" }
  | { kind: "processing"; performance: any }
  | { kind: "failed"; performance: any }
  | { kind: "reshoot"; performance: any; reason: string }
  | { kind: "ready"; performance: any; headline: string }
  | { kind: "readyGeneric"; performance: any };

export function deriveHomeHeroState(latestPerformance: any): HomeHeroState {
  if (!latestPerformance) return { kind: "first" };

  const status = latestPerformance.upload_status;

  if (status === "failed") {
    return { kind: "failed", performance: latestPerformance };
  }

  if (status !== "completed") {
    return { kind: "processing", performance: latestPerformance };
  }

  const summary = extractAnalysisSummary(latestPerformance.analysis_result);

  if (!summary?.biomechanicsReady) {
    const reason =
      (latestPerformance.analysis_result as any)?.biomechanics?.reason ??
      "This recording didn't meet the movement-reading requirements this time.";

    return { kind: "reshoot", performance: latestPerformance, reason };
  }

  const headline = buildReportHeadline(latestPerformance.analysis_result);

  return headline
    ? { kind: "ready", performance: latestPerformance, headline }
    : { kind: "readyGeneric", performance: latestPerformance };
}

export function HeroCard({ state }: { state: HomeHeroState }) {
  const navigate = useNavigate();
  const retryAnalysis = useRetryAnalysis();

  function handleRetry(performance: any) {
    if (!performance.video_url) return;
    retryAnalysis.retry({ performanceId: performance.id, videoPath: performance.video_url });
    navigate(ROUTES.ATHLETE.PERFORMANCE_PROCESSING(performance.id));
  }

  if (state.kind === "first") {
    return (
      <div className="flex flex-col gap-4 rounded-3xl border border-border-default bg-surface-sunken p-7">
        <h1 className="max-w-lg text-2xl font-bold leading-tight text-text-primary md:text-3xl">
          Ready for your first session?
        </h1>
        <p className="max-w-md text-[15px] leading-6 text-text-secondary">
          Record a short clip of your run or jump. We turn it into your first
          report in a few minutes.
        </p>
        <Link
          to={ROUTES.ATHLETE.NEW_PERFORMANCE}
          className="inline-flex w-fit items-center gap-2 rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover"
        >
          Record or upload a clip
          <ArrowRight className="h-4 w-4" />
        </Link>
        <p className="text-xs text-text-muted">Takes about two minutes.</p>
      </div>
    );
  }

  const { performance } = state;

  if (state.kind === "processing") {
    return (
      <div className="flex flex-col gap-4 rounded-3xl border border-border-default bg-surface-sunken p-7">
        <h1 className="max-w-lg text-2xl font-bold leading-tight text-text-primary md:text-3xl">
          We're reading your last performance
        </h1>
        <p className="max-w-md text-[15px] leading-6 text-text-secondary">
          This usually takes a couple of minutes. We'll let you know the
          moment it's ready.
        </p>
        <Link
          to={ROUTES.ATHLETE.PERFORMANCE_PROCESSING(performance.id)}
          className="inline-flex w-fit items-center gap-2 rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover"
        >
          <Loader2 className="h-4 w-4 animate-spin" />
          View status
        </Link>
      </div>
    );
  }

  if (state.kind === "failed") {
    return (
      <div className="flex flex-col gap-4 rounded-3xl border border-border-default bg-surface-sunken p-7">
        <h1 className="max-w-lg text-2xl font-bold leading-tight text-text-primary md:text-3xl">
          We couldn't finish your last analysis
        </h1>
        <p className="max-w-md text-[15px] leading-6 text-text-secondary">
          {friendlyErrorMessage(
            new Error(performance.analysis_error ?? ""),
            "analysis",
          )}
        </p>
        <div className="flex flex-wrap items-center gap-4">
          <button
            type="button"
            onClick={() => handleRetry(performance)}
            disabled={retryAnalysis.isPending}
            className="inline-flex items-center gap-2 rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${retryAnalysis.isPending ? "animate-spin" : ""}`} />
            {retryAnalysis.isPending ? "Retrying..." : "Retry analysis"}
          </button>
          <Link
            to={ROUTES.ATHLETE.PERFORMANCE_REPORT(performance.id)}
            className="text-sm font-semibold text-brand-action hover:text-brand-action-hover"
          >
            View details
          </Link>
        </div>
      </div>
    );
  }

  if (state.kind === "reshoot") {
    return (
      <div className="flex flex-col gap-4 rounded-3xl border border-border-default bg-surface-sunken p-7">
        <h1 className="max-w-lg text-2xl font-bold leading-tight text-text-primary md:text-3xl">
          We couldn't read your last run
        </h1>
        <p className="max-w-md text-[15px] leading-6 text-text-secondary">
          {state.reason}
        </p>
        <p className="text-xs text-text-muted">
          This is common early on - most athletes need a try or two to get the
          camera right.
        </p>
        <div className="flex flex-wrap items-center gap-4">
          <Link
            to={ROUTES.ATHLETE.NEW_PERFORMANCE}
            className="inline-flex items-center gap-2 rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover"
          >
            Try another recording
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            to={ROUTES.ATHLETE.PERFORMANCE_REPORT(performance.id)}
            className="text-sm font-semibold text-brand-action hover:text-brand-action-hover"
          >
            See the full breakdown
          </Link>
        </div>
      </div>
    );
  }

  // "ready" and "readyGeneric"
  const displayName = buildPerformanceDisplayName(performance);
  const chips = [
    CADENCE_METRIC.accessor(performance.analysis_result),
    STRIDE_FREQUENCY_METRIC.accessor(performance.analysis_result),
    DUTY_FACTOR_METRIC.accessor(performance.analysis_result),
  ];

  return (
    <div className="flex flex-col gap-4 rounded-3xl border border-border-default bg-surface-sunken p-7">
      <h1 className="max-w-lg text-2xl font-bold leading-tight text-text-primary md:text-3xl">
        {state.kind === "ready" ? state.headline : "Your report is ready"}
      </h1>
      <p className="max-w-md text-[15px] leading-6 text-text-secondary">
        From your {displayName} session on{" "}
        {formatSessionDate(performance.performance_date)}. Your full report has
        more on this.
      </p>
      <Link
        to={ROUTES.ATHLETE.PERFORMANCE_REPORT(performance.id)}
        className="inline-flex w-fit items-center gap-2 rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover"
      >
        See your full report
        <ArrowRight className="h-4 w-4" />
      </Link>

      {(chips[0] || chips[1] || chips[2]) && (
        <div className="flex flex-wrap gap-2">
          {chips[0] && (
            <span className="inline-flex items-baseline gap-1.5 rounded-lg border border-border-default bg-surface-card px-3 py-2 text-sm">
              <span className="font-['JetBrains_Mono'] font-semibold text-text-primary">
                {CADENCE_METRIC.format(chips[0])}
              </span>
            </span>
          )}
          {chips[1] && (
            <span className="inline-flex items-baseline gap-1.5 rounded-lg border border-border-default bg-surface-card px-3 py-2 text-sm">
              <span className="font-['JetBrains_Mono'] font-semibold text-text-primary">
                {STRIDE_FREQUENCY_METRIC.format(chips[1])}
              </span>
              <span className="text-xs text-text-muted">stride freq.</span>
            </span>
          )}
          {chips[2] && (
            <span className="inline-flex items-baseline gap-1.5 rounded-lg border border-border-default bg-surface-card px-3 py-2 text-sm">
              <span className="font-['JetBrains_Mono'] font-semibold text-text-primary">
                {DUTY_FACTOR_METRIC.format(chips[2])}
              </span>
              <span className="text-xs text-text-muted">duty factor</span>
              <span className="rounded border border-border-default px-1 font-['JetBrains_Mono'] text-[9px] uppercase tracking-wide text-text-muted">
                Experimental
              </span>
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default function AthleteHome() {
  const { user } = useAuth();

  const {
    data: performances = [],
    isLoading,
    error,
  } = useAthleteDashboard(user?.id);

  const { data: profileData } = useAthleteProfile(user?.id);
  const { data: goals = [] } = useAthleteGoals(user?.id);
  const { notifications } = useAthleteNotifications();

  const email = user?.email ?? "";
  const fullName = profileData?.base?.full_name?.trim();
  const displayName = fullName || email.split("@")[0] || "Athlete";
  const sporting = profileData?.sporting;
  const activeGoal = goals.find((goal) => goal.status === "active");

  const latestPerformance = performances[0];
  const recentPerformances = performances.slice(0, 5);

  const heroState = useMemo(
    () => deriveHomeHeroState(latestPerformance),
    [latestPerformance],
  );

  const twinConfidence = useMemo(
    () => computeTwinConfidence(performances.map(toTwinSessionInput)),
    [performances],
  );

  return (
    <div className="mx-auto max-w-6xl">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <p className="text-base font-semibold text-text-secondary">
          {getGreeting()}, {displayName}
        </p>

        <Link
          to={ROUTES.ATHLETE.NEW_PERFORMANCE}
          className="inline-flex w-fit items-center gap-2 rounded-xl border border-border-default px-4 py-2.5 text-sm font-semibold text-text-secondary transition hover:border-brand-action hover:text-brand-action"
        >
          <Plus className="h-4 w-4" />
          New performance
        </Link>
      </div>

      {error && (
        <div className="mt-6 rounded-3xl border border-error-failure bg-error-failure-soft p-5 text-sm leading-6 text-error-failure">
          {friendlyErrorMessage(error, "dashboard")}
        </div>
      )}

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
        <div className="flex flex-col gap-6">
          {isLoading ? (
            <div className="flex min-h-40 items-center justify-center rounded-3xl border border-border-default bg-surface-sunken p-7">
              <Loader2 className="h-6 w-6 animate-spin text-brand-action" />
            </div>
          ) : (
            <HeroCard state={heroState} />
          )}

          <section>
            <div className="flex items-center justify-between">
              <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.15em] text-text-muted">
                Recent sessions
              </p>

              {performances.length > 0 && (
                <Link
                  to={ROUTES.ATHLETE.HISTORY}
                  className="inline-flex items-center gap-1 text-sm font-semibold text-brand-action hover:text-brand-action-hover"
                >
                  View full history
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              )}
            </div>

            {isLoading ? (
              <div className="mt-3 flex items-center gap-3 rounded-2xl border border-border-default p-6 text-sm font-semibold text-text-secondary">
                <Loader2 className="h-5 w-5 animate-spin text-brand-action" />
                Loading recent sessions...
              </div>
            ) : recentPerformances.length > 0 ? (
              <div className="mt-3 divide-y divide-border-divider rounded-2xl border border-border-default">
                {recentPerformances.map((performance) => {
                  const summary = extractAnalysisSummary(performance.analysis_result);
                  const isCompleted = performance.upload_status === "completed";

                  return (
                    <Link
                      key={performance.id}
                      to={ROUTES.ATHLETE.PERFORMANCE_REPORT(performance.id)}
                      className="flex flex-col justify-between gap-3 p-4 transition hover:bg-surface-sunken sm:flex-row sm:items-center"
                    >
                      <div>
                        <p className="font-['JetBrains_Mono'] text-xs font-semibold tracking-[0.03em] text-brand-action-ink">
                          Performance #{String(performance.performance_number ?? 0).padStart(2, "0")}
                        </p>
                        <p className="mt-1 font-bold text-text-primary">
                          {buildPerformanceDisplayName(performance)}
                        </p>
                        <p className="mt-1 flex items-center gap-2 text-sm text-text-muted">
                          <CalendarDays className="h-3.5 w-3.5" />
                          {getEventName(performance.events)} ·{" "}
                          {formatSessionDate(performance.performance_date)}
                        </p>
                      </div>

                      {isCompleted ? (
                        <RatingBadge rating={summary?.rating} />
                      ) : (
                        <span
                          className={`w-fit rounded-full px-3 py-1 text-xs font-bold ${getStatusClasses(
                            performance.upload_status,
                          )}`}
                        >
                          {getStatusLabel(performance.upload_status)}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </div>
            ) : (
              <div className="mt-3 rounded-2xl border border-dashed border-border-default bg-surface-sunken p-8 text-center">
                <p className="text-sm font-semibold text-text-primary">
                  No sessions yet.
                </p>
                <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-text-muted">
                  Start your first session to build your timeline and prepare
                  your first report.
                </p>
              </div>
            )}
          </section>
        </div>

        <div className="flex flex-col gap-4">
          <div className="rounded-2xl border border-border-default bg-surface-sunken p-5">
            <p className="text-sm font-medium text-text-secondary">
              Personal best
            </p>

            {sporting?.personal_best ? (
              <p className="mt-3 text-lg font-bold text-text-primary">
                {sporting.personal_best}
              </p>
            ) : (
              <p className="mt-3 text-sm leading-6 text-text-muted">
                Not set yet.
              </p>
            )}

            <Link
              to={ROUTES.ATHLETE.PROFILE}
              className="mt-2 inline-flex items-center gap-1 text-sm font-semibold text-brand-action hover:text-brand-action-hover"
            >
              {sporting?.personal_best ? "Update" : "Add your personal best"}
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="rounded-2xl border border-border-default bg-surface-sunken p-5">
            <p className="text-sm font-medium text-text-secondary">
              Current goal
            </p>

            {activeGoal ? (
              <>
                <p className="mt-3 text-lg font-bold text-text-primary">
                  {activeGoal.description}
                </p>
                {formatTargetDate(activeGoal.target_date) && (
                  <p className="mt-1 text-sm text-text-muted">
                    Target: {formatTargetDate(activeGoal.target_date)}
                  </p>
                )}
              </>
            ) : (
              <p className="mt-3 text-sm leading-6 text-text-muted">
                No active goal yet.
              </p>
            )}

            <Link
              to={ROUTES.ATHLETE.GOALS}
              className="mt-2 inline-flex items-center gap-1 text-sm font-semibold text-brand-action hover:text-brand-action-hover"
            >
              {activeGoal ? "View goals" : "Set a goal"}
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="rounded-2xl border border-border-default bg-surface-card p-5">
            <p className="text-sm font-semibold text-text-primary">
              My Progress
            </p>

            {twinConfidence ? (
              <>
                <p className="mt-1 text-xs text-text-muted">
                  {CONFIDENCE_LABEL[twinConfidence.level]} —{" "}
                  {twinConfidence.sessionCount} session
                  {twinConfidence.sessionCount === 1 ? "" : "s"} so far
                </p>
                <div className="mt-3 flex gap-1" aria-hidden="true">
                  {[1, 2, 3].map((step) => (
                    <div
                      key={step}
                      className={`h-2 w-2 rounded-sm ${
                        step <= CONFIDENCE_STEP_COUNT[twinConfidence.level]
                          ? step === 1
                            ? "bg-text-disabled"
                            : step === 2
                              ? "bg-brand-action-hover"
                              : "bg-brand-action"
                          : "bg-border-default"
                      }`}
                    />
                  ))}
                </div>
              </>
            ) : (
              <p className="mt-2 text-sm leading-6 text-text-muted">
                Complete your first fully analyzed session to start building
                your progress picture.
              </p>
            )}

            <Link
              to={ROUTES.ATHLETE.TWIN}
              className="mt-3 inline-flex items-center gap-1 text-sm font-semibold text-brand-action hover:text-brand-action-hover"
            >
              View My Progress
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="rounded-2xl border border-border-default bg-surface-card p-5">
            <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.15em] text-text-muted">
              Notifications
            </p>

            {notifications.length === 0 ? (
              <p className="mt-3 text-sm leading-6 text-text-muted">
                You're all caught up - nothing new to review.
              </p>
            ) : (
              <div className="mt-3 flex flex-col gap-3">
                {notifications.slice(0, 4).map((notification) => {
                  const Icon = notificationIcon(notification.type);

                  return (
                    <Link
                      key={notification.id}
                      to={notification.href}
                      className="flex items-start gap-2 transition hover:opacity-70"
                    >
                      <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-action" />
                      <div>
                        <p className="text-sm font-bold text-text-primary">
                          {notification.title}
                        </p>
                        <p className="text-xs text-text-muted">
                          {notification.description}
                        </p>
                      </div>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
