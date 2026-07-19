import { Bell, ShieldAlert, Target, Users } from "lucide-react";
import type { EnrichedAthleteConnection } from "../../partners/hooks/useAthleteConnections";
import { getConnectionViewState } from "../../partners/lib/getConnectionViewState";

// "guardian_approval_required" has no backing system yet (no guardian
// relationships exist anywhere in the schema) - it's defined here, and
// never emitted, purely so a future guardian feature doesn't need to
// touch this type or any code that switches over it.
export type NotificationType =
  | "analysis_completed"
  | "recording_quality_insufficient"
  | "coach_connection_request"
  | "goal_target_date"
  | "guardian_approval_required";

// Shared between the Home notifications card and the navbar dropdown -
// one mapping from notification type to icon, not two copies drifting.
export function notificationIcon(type: NotificationType) {
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

export interface AthleteNotification {
  id: string;
  type: NotificationType;
  title: string;
  description: string;
  createdAt: string;
  href: string;
}

interface PerformanceLike {
  id: string;
  title: string;
  upload_status: string | null;
  updated_at: string | null;
  created_at: string | null;
  analysis_result: { biomechanics?: { status?: string; reason?: string } } | null;
}

interface GoalLike {
  id: string;
  description: string;
  target_date: string | null;
  status: string;
}

function performanceReportHref(performanceId: string): string {
  return `/console/athlete/performances/${performanceId}`;
}

const GOAL_REMINDER_WINDOW_DAYS = 7;
const MS_PER_DAY = 24 * 60 * 60 * 1000;

// Only active goals with a target date get a reminder - completed/
// abandoned goals are done, and a goal with no target date has nothing
// to remind about. `now` is a parameter (not `new Date()` inline) so
// this stays a pure, deterministically-testable function like the rest
// of this file.
function deriveGoalNotifications(goals: GoalLike[], now: Date): AthleteNotification[] {
  const notifications: AthleteNotification[] = [];
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  for (const goal of goals) {
    if (goal.status !== "active" || !goal.target_date) continue;

    const targetDate = new Date(goal.target_date);
    const dueDate = new Date(targetDate.getFullYear(), targetDate.getMonth(), targetDate.getDate());
    const daysUntilDue = Math.round((dueDate.getTime() - today.getTime()) / MS_PER_DAY);

    const formattedDate = new Intl.DateTimeFormat("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    }).format(targetDate);

    if (daysUntilDue < 0) {
      notifications.push({
        id: `goal-overdue-${goal.id}`,
        type: "goal_target_date",
        title: "Goal target date passed",
        description: `"${goal.description}" was due on ${formattedDate} - update its status or set a new target.`,
        createdAt: now.toISOString(),
        href: "/console/athlete/goals",
      });
    } else if (daysUntilDue <= GOAL_REMINDER_WINDOW_DAYS) {
      notifications.push({
        id: `goal-upcoming-${goal.id}`,
        type: "goal_target_date",
        title: "Goal target date approaching",
        description: `"${goal.description}" is due on ${formattedDate}.`,
        createdAt: now.toISOString(),
        href: "/console/athlete/goals",
      });
    }
  }

  return notifications;
}

export function deriveNotifications(
  performances: PerformanceLike[],
  connections: EnrichedAthleteConnection[],
  viewerId?: string,
  goals: GoalLike[] = [],
  now: Date = new Date(),
): AthleteNotification[] {
  const notifications: AthleteNotification[] = [...deriveGoalNotifications(goals, now)];

  for (const performance of performances) {
    if (performance.upload_status !== "completed") continue;

    const timestamp = performance.updated_at ?? performance.created_at ?? "";

    notifications.push({
      id: `analysis-completed-${performance.id}`,
      type: "analysis_completed",
      title: "Analysis complete",
      description: `Your report for "${performance.title}" is ready.`,
      createdAt: timestamp,
      href: performanceReportHref(performance.id),
    });

    const biomechanics = performance.analysis_result?.biomechanics;
    if (biomechanics?.status === "skipped") {
      notifications.push({
        id: `quality-insufficient-${performance.id}`,
        type: "recording_quality_insufficient",
        title: "Recording quality issue",
        description:
          biomechanics.reason ??
          `Biomechanics analysis was skipped for "${performance.title}".`,
        createdAt: timestamp,
        href: performanceReportHref(performance.id),
      });
    }
  }

  if (viewerId) {
    for (const connection of connections) {
      if (getConnectionViewState(connection, viewerId) !== "incoming_request") continue;

      notifications.push({
        id: `connection-request-${connection.id}`,
        type: "coach_connection_request",
        title: "Coach connection request",
        description: `${connection.partnerProfile?.full_name ?? "A coach or academy"} wants to connect.`,
        createdAt: connection.requested_at,
        href: "/console/athlete/coaches",
      });
    }
  }

  return notifications.sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
  );
}
