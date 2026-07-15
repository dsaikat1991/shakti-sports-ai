import { describe, expect, it } from "vitest";

import { getConnectionViewState } from "./getConnectionViewState";
import type { ConnectionInitiator, ConnectionStatus } from "../types/connection";

const COACH_ID = "coach-1";
const ATHLETE_ID = "athlete-1";

function connection(status: ConnectionStatus, initiatedBy: ConnectionInitiator) {
  return {
    status,
    initiated_by: initiatedBy,
    coach_id: COACH_ID,
    athlete_id: ATHLETE_ID,
  };
}

// Covers every combination of connection status x who initiated it x
// which side is viewing - the same row reads differently depending on
// perspective (a request I sent looks different from one I need to
// respond to), which is exactly what this pure function exists to
// resolve for both PartnerRequests.tsx and AthleteCoaches.tsx.
describe("getConnectionViewState", () => {
  it("is 'outgoing_request' for the coach who sent a pending invite", () => {
    const c = connection("pending", "coach");
    expect(getConnectionViewState(c, COACH_ID)).toBe("outgoing_request");
  });

  it("is 'incoming_request' for the athlete who received a coach-initiated invite", () => {
    const c = connection("pending", "coach");
    expect(getConnectionViewState(c, ATHLETE_ID)).toBe("incoming_request");
  });

  it("is 'outgoing_request' for the athlete who sent a pending invite", () => {
    const c = connection("pending", "athlete");
    expect(getConnectionViewState(c, ATHLETE_ID)).toBe("outgoing_request");
  });

  it("is 'incoming_request' for the coach who received an athlete-initiated invite", () => {
    const c = connection("pending", "athlete");
    expect(getConnectionViewState(c, COACH_ID)).toBe("incoming_request");
  });

  it("is 'connected' for either party once accepted", () => {
    const c = connection("accepted", "coach");
    expect(getConnectionViewState(c, COACH_ID)).toBe("connected");
    expect(getConnectionViewState(c, ATHLETE_ID)).toBe("connected");
  });

  it("is 'declined' for either party once rejected", () => {
    const c = connection("rejected", "coach");
    expect(getConnectionViewState(c, COACH_ID)).toBe("declined");
    expect(getConnectionViewState(c, ATHLETE_ID)).toBe("declined");
  });

  it("is 'ended' for either party once revoked", () => {
    const c = connection("revoked", "coach");
    expect(getConnectionViewState(c, COACH_ID)).toBe("ended");
    expect(getConnectionViewState(c, ATHLETE_ID)).toBe("ended");
  });
});
