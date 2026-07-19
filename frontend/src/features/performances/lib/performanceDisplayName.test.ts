import { describe, expect, it } from "vitest";
import { buildPerformanceDisplayName } from "./performanceDisplayName";

describe("buildPerformanceDisplayName", () => {
  it("renders from performance_type and date/event alone when there is no personal note or internal number to lean on", () => {
    const name = buildPerformanceDisplayName({
      performance_type: "practice",
      title: "",
    });

    expect(name).toBe("Practice");
  });

  it("appends the athlete's personal note as a quoted suffix when present", () => {
    const name = buildPerformanceDisplayName({
      performance_type: "practice",
      title: "Felt amazing today",
    });

    expect(name).toBe('Practice — "Felt amazing today"');
  });

  it("falls back to a generic label for rows that predate performance_type, still with the note", () => {
    const name = buildPerformanceDisplayName({
      performance_type: null,
      title: "Old session before the column existed",
    });

    expect(name).toBe('Session — "Old session before the column existed"');
  });

  it("falls back to a generic label with no note for legacy rows with neither field", () => {
    const name = buildPerformanceDisplayName({
      performance_type: null,
      title: "",
    });

    expect(name).toBe("Session");
  });

  it("trims whitespace-only personal notes rather than rendering an empty quoted suffix", () => {
    const name = buildPerformanceDisplayName({
      performance_type: "competition",
      title: "   ",
    });

    expect(name).toBe("Competition");
  });

  it("labels every performance_type correctly", () => {
    expect(buildPerformanceDisplayName({ performance_type: "trial", title: "" })).toBe("Trial");
    expect(buildPerformanceDisplayName({ performance_type: "assessment", title: "" })).toBe(
      "Assessment",
    );
  });
});
