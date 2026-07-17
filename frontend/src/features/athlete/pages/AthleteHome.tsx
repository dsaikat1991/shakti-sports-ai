import {
  ArrowRight,
  Bell,
  CalendarDays,
  CheckCircle2,
  Clock3,
  FileVideo,
  Loader2,
  Plus,
  ShieldAlert,
  Target,
  Trophy,
  Users,
} from "lucide-react";
import { Link } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { useAthleteDashboard } from "../hooks/useAthleteDashboard";
import { useAthleteProfile } from "../hooks/useAthleteProfile";
import { useAthleteGoals } from "../hooks/useAthleteGoals";
import { useAthleteNotifications } from "../hooks/useAthleteNotifications";
import type { NotificationType } from "../lib/deriveNotifications";
import { formatSessionDate } from "../../performances/lib/analysisSummary";

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

function getGreeting() {
  const hour = new Date().getHours();

  if (hour >= 5 && hour < 12) return "Good Morning";
  if (hour >= 12 && hour < 17) return "Good Afternoon";
  if (hour >= 17 && hour < 21) return "Good Evening";

  return "Good Night";
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

function getStatusClasses(status: string | null) {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-700";

    case "processing":
    case "analyzing":
      return "bg-blue-100 text-blue-700";

    case "failed":
      return "bg-red-100 text-red-700";

    default:
      return "bg-orange-100 text-[#F0600E]";
  }
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

  const totalPerformances = performances.length;

  const completedReports = performances.filter(
    (performance) => performance.upload_status === "completed",
  ).length;

  const thisMonthPerformances = performances.filter((performance) => {
    if (!performance.created_at) return false;

    const createdAt = new Date(performance.created_at);
    const now = new Date();

    return (
      createdAt.getMonth() === now.getMonth() &&
      createdAt.getFullYear() === now.getFullYear()
    );
  }).length;

  return (
    <div className="mx-auto max-w-6xl">
      <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
        <div>
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
            Performance Centre
          </p>

          <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
            {getGreeting()}, {displayName} 👋
          </h1>

          <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
            Start a new session, review recent performances, and track your
            progress as Shakti Motion Intelligence™ prepares your reports.
          </p>

          {sporting?.preferred_event && (
            <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-orange-200 bg-[#FFF8F3] px-4 py-2 text-xs font-bold uppercase tracking-widest text-[#F0600E]">
              <Trophy className="h-3.5 w-3.5" />
              {sporting.preferred_event}
              {sporting.academy && <span className="text-gray-400">· {sporting.academy}</span>}
            </div>
          )}
        </div>

        <Link
          to={ROUTES.ATHLETE.NEW_PERFORMANCE}
          className="inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-xl bg-[#F0600E] px-6 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
        >
          Start New Performance
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {error && (
        <div className="mt-8 rounded-3xl border border-red-200 bg-red-50 p-5 text-sm font-semibold text-red-700">
          {error.message}
        </div>
      )}

      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-gray-600">
              Total Performances
            </p>

            <FileVideo className="h-5 w-5 text-[#F0600E]" />
          </div>

          <p className="mt-5 font-['Anton'] text-5xl text-gray-950">
            {isLoading ? "—" : totalPerformances}
          </p>

          <p className="mt-2 text-sm text-gray-500">
            Sessions saved to your timeline
          </p>
        </div>

        <div className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-gray-600">This Month</p>

            <CalendarDays className="h-5 w-5 text-[#F0600E]" />
          </div>

          <p className="mt-5 font-['Anton'] text-5xl text-gray-950">
            {isLoading ? "—" : thisMonthPerformances}
          </p>

          <p className="mt-2 text-sm text-gray-500">
            Performances uploaded this month
          </p>
        </div>

        <div className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-gray-600">Latest Upload</p>

            <Clock3 className="h-5 w-5 text-[#F0600E]" />
          </div>

          <p className="mt-5 font-['Anton'] text-5xl text-gray-950">
            {latestPerformance?.performance_number
              ? `#${String(latestPerformance.performance_number).padStart(
                  2,
                  "0",
                )}`
              : "—"}
          </p>

          <p className="mt-2 truncate text-sm text-gray-500">
            {latestPerformance?.title ?? "No performance uploaded"}
          </p>
        </div>

        <div className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-gray-600">Reports Ready</p>

            <CheckCircle2 className="h-5 w-5 text-green-700" />
          </div>

          <p className="mt-5 font-['Anton'] text-5xl text-gray-950">
            {isLoading ? "—" : completedReports}
          </p>

          <p className="mt-2 text-sm text-gray-500">
            Completed AI performance reports
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Link
          to={ROUTES.ATHLETE.NEW_PERFORMANCE}
          className="group block rounded-4xl border border-orange-200 bg-[#FFF8F3] p-8 shadow-xl shadow-orange-100 transition duration-300 hover:-translate-y-1 hover:border-[#F0600E]"
        >
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#F0600E] text-white">
            <Plus className="h-7 w-7" />
          </div>

          <h2 className="mt-8 font-['Anton'] text-4xl uppercase leading-none text-gray-950">
            Start New Performance
          </h2>

          <p className="mt-4 max-w-xl text-sm leading-6 text-gray-600">
            Choose your event, add session details, upload your recording, and
            prepare it for Shakti Motion Intelligence™.
          </p>

          <div className="mt-8 flex items-center gap-2 text-sm font-black text-[#F0600E]">
            Begin Session
            <ArrowRight className="h-4 w-4 transition duration-300 group-hover:translate-x-1" />
          </div>
        </Link>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-xl shadow-gray-200/70">
          <div className="flex items-center justify-between">
            <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
              Latest Performance
            </p>

            {latestPerformance && (
              <span
                className={`rounded-full px-3 py-1 text-xs font-bold ${getStatusClasses(
                  latestPerformance.upload_status,
                )}`}
              >
                {getStatusLabel(latestPerformance.upload_status)}
              </span>
            )}
          </div>

          {isLoading ? (
            <div className="flex min-h-52 items-center justify-center">
              <Loader2 className="h-7 w-7 animate-spin text-[#F0600E]" />
            </div>
          ) : latestPerformance ? (
            <>
              <p className="mt-5 font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
                Performance #
                {String(
                  latestPerformance.performance_number ?? 0,
                ).padStart(2, "0")}
              </p>

              <h3 className="mt-2 text-2xl font-bold text-gray-950">
                {latestPerformance.title}
              </h3>

              <p className="mt-2 flex items-center gap-2 text-sm text-gray-500">
                <CalendarDays className="h-4 w-4" />
                {formatSessionDate(latestPerformance.performance_date)} ·{" "}
                {getEventName(latestPerformance.events)}
              </p>

              <Link
                to={ROUTES.ATHLETE.PERFORMANCE_PROCESSING(
                  latestPerformance.id,
                )}
                className="mt-8 inline-flex items-center gap-2 text-sm font-bold text-[#F0600E] transition hover:text-orange-700"
              >
                View Performance
                <ArrowRight className="h-4 w-4" />
              </Link>
            </>
          ) : (
            <div className="flex min-h-52 flex-col items-center justify-center text-center">
              <FileVideo className="h-9 w-9 text-gray-300" />

              <h3 className="mt-4 text-lg font-bold text-gray-950">
                No performance uploaded
              </h3>

              <p className="mt-2 max-w-sm text-sm leading-6 text-gray-500">
                Your latest session will appear here after your first upload.
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
              Recent Performances
            </p>

            <h2 className="mt-2 text-2xl font-bold text-gray-950">
              Your latest sessions
            </h2>
          </div>

          {performances.length > 0 && (
            <Link
              to={ROUTES.ATHLETE.HISTORY}
              className="inline-flex items-center gap-2 text-sm font-bold text-[#F0600E] transition hover:text-orange-700"
            >
              View Full History
              <ArrowRight className="h-4 w-4" />
            </Link>
          )}
        </div>

        {isLoading ? (
          <div className="mt-6 flex items-center gap-3 rounded-3xl bg-gray-50 p-6 text-sm font-semibold text-gray-600">
            <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
            Loading recent performances...
          </div>
        ) : recentPerformances.length > 0 ? (
          <div className="mt-6 divide-y divide-gray-100">
            {recentPerformances.map((performance) => (
              <div
                key={performance.id}
                className="flex flex-col justify-between gap-4 py-5 first:pt-0 last:pb-0 md:flex-row md:items-center"
              >
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.18em] text-[#F0600E]">
                      Performance #
                      {String(
                        performance.performance_number ?? 0,
                      ).padStart(2, "0")}
                    </p>

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-bold ${getStatusClasses(
                        performance.upload_status,
                      )}`}
                    >
                      {getStatusLabel(performance.upload_status)}
                    </span>
                  </div>

                  <h3 className="mt-2 text-lg font-bold text-gray-950">
                    {performance.title}
                  </h3>

                  <p className="mt-1 text-sm text-gray-500">
                    {getEventName(performance.events)} ·{" "}
                    {formatSessionDate(performance.performance_date)}
                  </p>
                </div>

                <Link
                  to={ROUTES.ATHLETE.PERFORMANCE_REPORT(performance.id)}
                  className="inline-flex items-center gap-2 text-sm font-bold text-gray-700 transition hover:text-[#F0600E]"
                >
                  View Status
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-6 rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
            <FileVideo className="mx-auto h-10 w-10 text-gray-400" />

            <h3 className="mt-4 text-lg font-bold text-gray-950">
              No performances yet.
            </h3>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
              Start your first performance to build your timeline and prepare
              your first AI report.
            </p>

            <Link
              to={ROUTES.ATHLETE.NEW_PERFORMANCE}
              className="mt-5 inline-flex items-center justify-center rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
            >
              Start First Performance
            </Link>
          </div>
        )}
      </div>

      <div className="mt-6 grid gap-6 md:grid-cols-3">
        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <Trophy className="h-5 w-5 text-[#F0600E]" />
            <h3 className="font-bold text-gray-950">Personal Best</h3>
          </div>

          {sporting?.personal_best ? (
            <p className="mt-5 text-2xl font-bold text-gray-950">
              {sporting.personal_best}
            </p>
          ) : (
            <p className="mt-5 text-sm leading-6 text-gray-500">
              Not set yet.
            </p>
          )}

          <Link
            to={ROUTES.ATHLETE.PROFILE}
            className="mt-4 inline-flex items-center gap-1 text-sm font-bold text-[#F0600E] hover:text-orange-700"
          >
            {sporting?.personal_best ? "Update" : "Add your personal best"}
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="h-5 w-5 text-green-700" />
            <h3 className="font-bold text-gray-950">Recording Quality</h3>
          </div>

          {latestPerformance?.analysis_result ? (
            <>
              <p className="mt-5 text-2xl font-bold text-gray-950">
                {(latestPerformance.analysis_result as any)?.recording_quality?.rating ?? "N/A"}
              </p>
              <p className="mt-2 text-sm leading-6 text-gray-500">
                From your latest analyzed session.
              </p>
            </>
          ) : (
            <p className="mt-5 text-sm leading-6 text-gray-500">
              Complete an analysis to see your recording quality here.
            </p>
          )}
        </div>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <Target className="h-5 w-5 text-[#F0600E]" />
            <h3 className="font-bold text-gray-950">Current Goal</h3>
          </div>

          {activeGoal ? (
            <>
              <p className="mt-5 font-bold text-gray-950">{activeGoal.description}</p>
              {formatTargetDate(activeGoal.target_date) && (
                <p className="mt-2 text-sm text-gray-500">
                  Target: {formatTargetDate(activeGoal.target_date)}
                </p>
              )}
            </>
          ) : (
            <p className="mt-5 text-sm leading-6 text-gray-500">
              No active goal yet.
            </p>
          )}

          <Link
            to={ROUTES.ATHLETE.GOALS}
            className="mt-4 inline-flex items-center gap-1 text-sm font-bold text-[#F0600E] hover:text-orange-700"
          >
            {activeGoal ? "View goals" : "Set a goal"}
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>

      <div className="mt-6 rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <Bell className="h-5 w-5 text-[#F0600E]" />
          <h3 className="font-bold text-gray-950">Notifications</h3>
        </div>

        {notifications.length === 0 ? (
          <p className="mt-5 text-sm leading-6 text-gray-500">
            You're all caught up - nothing new to review.
          </p>
        ) : (
          <div className="mt-5 divide-y divide-gray-100">
            {notifications.slice(0, 5).map((notification) => {
              const Icon = notificationIcon(notification.type);

              return (
                <Link
                  key={notification.id}
                  to={notification.href}
                  className="flex items-start gap-3 py-3 first:pt-0 last:pb-0 transition hover:opacity-70"
                >
                  <Icon className="mt-0.5 h-4 w-4 shrink-0 text-[#F0600E]" />
                  <div>
                    <p className="text-sm font-bold text-gray-950">{notification.title}</p>
                    <p className="text-sm text-gray-500">{notification.description}</p>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}