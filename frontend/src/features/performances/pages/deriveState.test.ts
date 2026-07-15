import { describe, expect, it } from "vitest";

import { deriveState } from "./PerformanceProcessing";

// Covers every state the job-status workflow can actually be in
// (upload pending / queued / processing / completed / failed / retry
// available via "failed" / timed out), as a pure-function unit test
// rather than mounting the full page (which needs router + query-client
// + auth context to render at all).
describe("deriveState", () => {
  it("is 'not_started' immediately after upload, before the backend has reported anything", () => {
    expect(deriveState("analyzing", undefined, false)).toBe("not_started");
  });

  it("is 'queued' once the backend confirms the job is queued", () => {
    expect(deriveState("analyzing", "queued", false)).toBe("queued");
  });

  it("is 'processing' once the backend starts running analysis", () => {
    expect(deriveState("analyzing", "processing", false)).toBe("processing");
  });

  it("is 'completed' when the Supabase row says so, even before a fresh poll confirms it", () => {
    expect(deriveState("completed", undefined, false)).toBe("completed");
  });

  it("is 'completed' the instant the live poll reports it, before the Supabase write lands", () => {
    expect(deriveState("analyzing", "completed", false)).toBe("completed");
  });

  it("is 'failed' when the Supabase row says so", () => {
    expect(deriveState("failed", undefined, false)).toBe("failed");
  });

  it("is 'failed' the instant the live poll reports it", () => {
    expect(deriveState("analyzing", "failed", false)).toBe("failed");
  });

  it("completed takes priority over a stale failed row state", () => {
    // Can happen right after a retry: the row was "failed" from the
    // previous attempt, but the new job has already completed and the
    // Supabase write-back just hasn't landed yet.
    expect(deriveState("failed", "completed", false)).toBe("completed");
  });

  it("is 'timed_out' once the elapsed-poll timeout trips, unless already terminal", () => {
    expect(deriveState("analyzing", "processing", true)).toBe("timed_out");
  });

  it("terminal states are never overridden by a timeout", () => {
    expect(deriveState("completed", undefined, true)).toBe("completed");
    expect(deriveState("failed", undefined, true)).toBe("failed");
  });
});
