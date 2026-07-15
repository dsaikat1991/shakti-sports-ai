import type { PartnerConnection } from "../types/connection";

// Which side of a connection row the current viewer is on, and what
// state that row is actually in from their perspective - a pending
// request the viewer sent looks different from one they need to
// respond to, even though it's the same underlying row.
export type ConnectionViewState =
  | "outgoing_request"
  | "incoming_request"
  | "connected"
  | "declined"
  | "ended";

type ConnectionSubset = Pick<
  PartnerConnection,
  "status" | "initiated_by" | "coach_id" | "athlete_id"
>;

export function getConnectionViewState(
  connection: ConnectionSubset,
  viewerId: string,
): ConnectionViewState {
  const viewerIsCoachSide = viewerId === connection.coach_id;
  const viewerIsInitiator =
    (connection.initiated_by === "coach" && viewerIsCoachSide) ||
    (connection.initiated_by === "athlete" && !viewerIsCoachSide);

  if (connection.status === "pending") {
    return viewerIsInitiator ? "outgoing_request" : "incoming_request";
  }

  if (connection.status === "accepted") {
    return "connected";
  }

  if (connection.status === "rejected") {
    return "declined";
  }

  return "ended";
}
