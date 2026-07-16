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
  | "guardian_approval_required";

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

function performanceReportHref(performanceId: string): string {
  return `/console/athlete/performances/${performanceId}`;
}

export function deriveNotifications(
  performances: PerformanceLike[],
  connections: EnrichedAthleteConnection[],
  viewerId?: string,
): AthleteNotification[] {
  const notifications: AthleteNotification[] = [];

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
