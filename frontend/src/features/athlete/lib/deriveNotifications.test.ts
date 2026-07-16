import { describe, expect, it } from "vitest";

import { deriveNotifications } from "./deriveNotifications";

function performance(overrides: Partial<Parameters<typeof deriveNotifications>[0][number]> = {}) {
  return {
    id: "perf-1",
    title: "Sprint Session",
    upload_status: "completed",
    updated_at: "2026-07-10T00:00:00Z",
    created_at: "2026-07-09T00:00:00Z",
    analysis_result: null,
    ...overrides,
  };
}

function goal(overrides: Record<string, unknown> = {}) {
  return {
    id: "goal-1",
    description: "Break 11.5s in the 100m",
    target_date: null,
    status: "active",
    ...overrides,
  };
}

function connection(overrides: Record<string, unknown> = {}) {
  return {
    id: "conn-1",
    coach_id: "coach-1",
    athlete_id: "athlete-1",
    partner_role: "coach",
    status: "pending",
    initiated_by: "coach",
    invited_email: null,
    requested_at: "2026-07-11T00:00:00Z",
    responded_at: null,
    created_at: "2026-07-11T00:00:00Z",
    partnerProfile: { id: "coach-1", full_name: "Coach Test", email: "coach@example.com", role: "coach" },
    ...overrides,
  } as any;
}

describe("deriveNotifications", () => {
  it("emits nothing for empty input", () => {
    expect(deriveNotifications([], [], "athlete-1")).toEqual([]);
  });

  it("ignores performances that aren't completed", () => {
    const result = deriveNotifications(
      [performance({ upload_status: "analyzing" })],
      [],
      "athlete-1",
    );
    expect(result).toEqual([]);
  });

  it("emits an analysis_completed notification for a completed performance", () => {
    const result = deriveNotifications([performance()], [], "athlete-1");
    expect(result).toHaveLength(1);
    expect(result[0].type).toBe("analysis_completed");
    expect(result[0].href).toBe("/console/athlete/performances/perf-1");
  });

  it("also emits recording_quality_insufficient when biomechanics was skipped", () => {
    const result = deriveNotifications(
      [
        performance({
          analysis_result: {
            biomechanics: { status: "skipped", reason: "Feet not visible enough." },
          },
        }),
      ],
      [],
      "athlete-1",
    );
    expect(result).toHaveLength(2);
    const qualityNotification = result.find((n) => n.type === "recording_quality_insufficient");
    expect(qualityNotification?.description).toBe("Feet not visible enough.");
  });

  it("does not emit recording_quality_insufficient when biomechanics succeeded", () => {
    const result = deriveNotifications(
      [performance({ analysis_result: { biomechanics: { status: "completed" } } })],
      [],
      "athlete-1",
    );
    expect(result.some((n) => n.type === "recording_quality_insufficient")).toBe(false);
  });

  it("emits a coach_connection_request only for incoming pending requests, not outgoing ones", () => {
    const incoming = connection({ initiated_by: "coach", status: "pending" });
    const outgoing = connection({ id: "conn-2", initiated_by: "athlete", status: "pending" });
    const accepted = connection({ id: "conn-3", status: "accepted" });

    const result = deriveNotifications([], [incoming, outgoing, accepted], "athlete-1");

    expect(result).toHaveLength(1);
    expect(result[0].type).toBe("coach_connection_request");
    expect(result[0].description).toContain("Coach Test");
  });

  it("sorts notifications newest first", () => {
    const older = performance({ id: "perf-old", updated_at: "2026-01-01T00:00:00Z" });
    const newer = performance({ id: "perf-new", updated_at: "2026-07-01T00:00:00Z" });

    const result = deriveNotifications([older, newer], [], "athlete-1");

    expect(result.map((n) => n.id)).toEqual([
      "analysis-completed-perf-new",
      "analysis-completed-perf-old",
    ]);
  });

  it("without a viewerId, skips connection-derived notifications entirely", () => {
    const incoming = connection({ initiated_by: "coach", status: "pending" });
    const result = deriveNotifications([], [incoming], undefined);
    expect(result).toEqual([]);
  });

  describe("goal target-date reminders", () => {
    const now = new Date("2026-07-16T12:00:00Z");

    it("emits nothing for an active goal with no target date", () => {
      const result = deriveNotifications([], [], "athlete-1", [goal()], now);
      expect(result).toEqual([]);
    });

    it("emits nothing for a target date far in the future", () => {
      const result = deriveNotifications(
        [],
        [],
        "athlete-1",
        [goal({ target_date: "2026-09-01" })],
        now,
      );
      expect(result).toEqual([]);
    });

    it("emits an upcoming reminder within the 7-day window", () => {
      const result = deriveNotifications(
        [],
        [],
        "athlete-1",
        [goal({ target_date: "2026-07-19" })],
        now,
      );
      expect(result).toHaveLength(1);
      expect(result[0].type).toBe("goal_target_date");
      expect(result[0].title).toBe("Goal target date approaching");
      expect(result[0].description).toContain("Break 11.5s in the 100m");
    });

    it("emits an overdue reminder once the target date has passed", () => {
      const result = deriveNotifications(
        [],
        [],
        "athlete-1",
        [goal({ target_date: "2026-07-10" })],
        now,
      );
      expect(result).toHaveLength(1);
      expect(result[0].title).toBe("Goal target date passed");
    });

    it("ignores completed/abandoned goals even with a near target date", () => {
      const result = deriveNotifications(
        [],
        [],
        "athlete-1",
        [
          goal({ target_date: "2026-07-17", status: "completed" }),
          goal({ id: "goal-2", target_date: "2026-07-17", status: "abandoned" }),
        ],
        now,
      );
      expect(result).toEqual([]);
    });
  });
});
