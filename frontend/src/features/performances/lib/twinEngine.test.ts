import { describe, expect, it } from "vitest";

import {
  analyzeTrend,
  buildTwinMetricTrend,
  buildTwinPersonalBests,
  computeConsistency,
  computeTwinConfidence,
  deriveDevelopmentAreas,
  deriveDevelopmentStage,
  deriveStrengths,
  dominantEventName,
  generateEvolutionStatements,
  groupByDominantProvider,
  traceMetricInclusion,
  type TwinSessionInput,
} from "./twinEngine";
import { METRIC_REGISTRY } from "./metricRegistry";

let idCounter = 0;

function buildSession(overrides: {
  date: string;
  cadence?: number;
  kneeSymmetry?: number;
  readiness?: number;
  detectionRate?: number;
  bodyVisibility?: number;
  provider?: string;
  biomechanicsSkipped?: boolean;
  uploadStatus?: string;
  event?: string;
  includeCadence?: boolean;
  cadenceExplicitNull?: boolean;
  leftKneeCoveragePercent?: number;
  id?: string;
}): TwinSessionInput {
  idCounter += 1;
  const {
    date,
    cadence = 180,
    kneeSymmetry = 90,
    readiness = 85,
    detectionRate = 95,
    bodyVisibility = 90,
    provider = "rtmpose",
    biomechanicsSkipped = false,
    uploadStatus = "completed",
    event = "Sprint",
    includeCadence = true,
    cadenceExplicitNull = false,
    leftKneeCoveragePercent = 80,
    id,
  } = overrides;

  const cadenceField = cadenceExplicitNull
    ? { steps_per_minute: null }
    : includeCadence
      ? { steps_per_minute: cadence }
      : {};

  return {
    id: id ?? `perf-${idCounter}`,
    performanceNumber: idCounter,
    performanceDate: date,
    createdAt: date,
    events: [{ name: event, category: "Athletics" }],
    uploadStatus,
    analysisResult: {
      provider,
      analysis: { detection_rate_percent: detectionRate },
      recording_quality: {
        rating: "Excellent",
        camera_view: { classification: "Side View" },
        analysis_readiness: { score: readiness },
        metrics: { full_body_visibility_score: bodyVisibility, athlete_movement_score: 85 },
      },
      biomechanics: biomechanicsSkipped
        ? { status: "skipped", reason: "Feet not visible enough." }
        : {
            status: "completed",
            segments: [
              {
                status: "completed",
                cadence: cadenceField,
                stride: { stride_frequency_hz: cadence / 120 },
                knee_symmetry_score: kneeSymmetry,
                ground_contact: { events: 40 },
                duty_factor_percent: 24,
                flight_time: { median_flight_time_ms: 130 },
                joint_angles: {
                  left_knee: { mean_degrees: 150, coverage_percent: leftKneeCoveragePercent },
                  right_knee: { mean_degrees: 148, coverage_percent: 82 },
                },
              },
            ],
          },
    },
  };
}

describe("groupByDominantProvider", () => {
  it("returns empty for no sessions", () => {
    const result = groupByDominantProvider([]);
    expect(result.dominant).toEqual([]);
    expect(result.dominantProvider).toBeNull();
    expect(result.excludedCount).toBe(0);
  });

  it("excludes minority-provider sessions instead of blending them", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", provider: "rtmpose" }),
      buildSession({ date: "2026-02-01", provider: "rtmpose" }),
      buildSession({ date: "2026-03-01", provider: "rtmpose" }),
      buildSession({ date: "2026-04-01", provider: "mediapipe" }),
    ];
    const result = groupByDominantProvider(sessions);
    expect(result.dominantProvider).toBe("rtmpose");
    expect(result.dominant).toHaveLength(3);
    expect(result.excludedCount).toBe(1);
  });
});

describe("buildTwinMetricTrend - insufficient data states", () => {
  const cadenceMetric = METRIC_REGISTRY.find((m) => m.key === "cadence")!;

  it("no completed analyses -> insufficient_data, 0 samples", () => {
    const { trend } = buildTwinMetricTrend([], cadenceMetric);
    expect(trend.samples).toBe(0);
    expect(trend.direction).toBe("insufficient_data");
  });

  it("exactly one valid analysis -> insufficient_data (below the 2-sample minimum)", () => {
    const sessions = [buildSession({ date: "2026-01-01" })];
    const { trend } = buildTwinMetricTrend(sessions, cadenceMetric);
    expect(trend.samples).toBe(1);
    expect(trend.direction).toBe("insufficient_data");
  });

  it("two or more comparable analyses -> a real trend", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", cadence: 170 }),
      buildSession({ date: "2026-03-01", cadence: 185 }),
    ];
    const { trend } = buildTwinMetricTrend(sessions, cadenceMetric);
    expect(trend.samples).toBe(2);
    expect(trend.direction).toBe("improving");
  });

  it("skipped biomechanics excludes that session from biomechanics metrics, not from recording-quality ones", () => {
    const readinessMetric = METRIC_REGISTRY.find((m) => m.key === "readiness_score")!;
    const sessions = [
      buildSession({ date: "2026-01-01", biomechanicsSkipped: true, readiness: 60 }),
      buildSession({ date: "2026-02-01", biomechanicsSkipped: true, readiness: 65 }),
      buildSession({ date: "2026-03-01", biomechanicsSkipped: false, readiness: 70 }),
    ];

    const cadenceTrend = buildTwinMetricTrend(sessions, cadenceMetric);
    expect(cadenceTrend.trend.samples).toBe(1); // only the one non-skipped session
    expect(cadenceTrend.trend.direction).toBe("insufficient_data");

    const readinessTrend = buildTwinMetricTrend(sessions, readinessMetric);
    expect(readinessTrend.trend.samples).toBe(3); // recording quality present regardless of biomechanics
  });

  it("a metric missing from most sessions still trends correctly on the sessions where it IS present", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", includeCadence: false }),
      buildSession({ date: "2026-02-01", cadence: 175 }),
      buildSession({ date: "2026-03-01", cadence: 190 }),
    ];
    const { trend } = buildTwinMetricTrend(sessions, cadenceMetric);
    expect(trend.samples).toBe(2); // the session missing cadence is excluded, not counted as 0
  });
});

describe("buildTwinPersonalBests", () => {
  it("empty for no completed sessions", () => {
    expect(buildTwinPersonalBests([])).toEqual([]);
  });

  it("never includes an experimental metric (ground contact / duty factor / flight time)", () => {
    const sessions = [buildSession({ date: "2026-01-01" }), buildSession({ date: "2026-02-01" })];
    const pbs = buildTwinPersonalBests(sessions);
    const keys = pbs.map((pb) => pb.metricKey);
    expect(keys).not.toContain("ground_contacts");
    expect(keys).not.toContain("duty_factor");
    expect(keys).not.toContain("flight_time");
  });

  it("a single session still produces a well-defined personal best", () => {
    const sessions = [buildSession({ date: "2026-01-01", cadence: 180 })];
    const pbs = buildTwinPersonalBests(sessions);
    const cadencePb = pbs.find((pb) => pb.metricKey === "cadence");
    expect(cadencePb?.value).toBe(180);
    expect(cadencePb?.performanceId).toBe(sessions[0].id);
  });

  it("picks the correct max across multiple sessions and links the originating performance", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", cadence: 170 }),
      buildSession({ date: "2026-02-01", cadence: 195 }),
      buildSession({ date: "2026-03-01", cadence: 180 }),
    ];
    const pbs = buildTwinPersonalBests(sessions);
    const cadencePb = pbs.find((pb) => pb.metricKey === "cadence");
    expect(cadencePb?.value).toBe(195);
    expect(cadencePb?.performanceId).toBe(sessions[1].id);
  });
});

describe("deriveStrengths / deriveDevelopmentAreas", () => {
  it("no observations from a single session (below the 2-sample minimum)", () => {
    const sessions = [buildSession({ date: "2026-01-01" })];
    expect(deriveStrengths(sessions)).toEqual([]);
    expect(deriveDevelopmentAreas(sessions)).toEqual([]);
  });

  it("flags a consistent, improving metric as a strength", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", cadence: 178 }),
      buildSession({ date: "2026-03-01", cadence: 182 }),
      buildSession({ date: "2026-06-01", cadence: 186 }),
    ];
    const strengths = deriveStrengths(sessions);
    expect(strengths.some((s) => s.key === "cadence-improving")).toBe(true);
  });

  it("flags a noisy metric as a development area, not a strength", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", kneeSymmetry: 60 }),
      buildSession({ date: "2026-02-01", kneeSymmetry: 95 }),
      buildSession({ date: "2026-03-01", kneeSymmetry: 55 }),
      buildSession({ date: "2026-04-01", kneeSymmetry: 92 }),
    ];
    const developmentAreas = deriveDevelopmentAreas(sessions);
    const strengths = deriveStrengths(sessions);
    expect(developmentAreas.some((a) => a.key === "knee_symmetry-inconsistent")).toBe(true);
    expect(strengths.some((s) => s.key === "knee_symmetry-consistent")).toBe(false);
  });

  it("flags low biomechanics availability as a development area", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", biomechanicsSkipped: true }),
      buildSession({ date: "2026-02-01", biomechanicsSkipped: true }),
      buildSession({ date: "2026-03-01", biomechanicsSkipped: true }),
      buildSession({ date: "2026-04-01", biomechanicsSkipped: false }),
    ];
    const developmentAreas = deriveDevelopmentAreas(sessions);
    expect(developmentAreas.some((a) => a.key === "biomechanics-availability")).toBe(true);
  });

  it("never derives a strength or development area from an experimental metric", () => {
    const sessions = [
      buildSession({ date: "2026-01-01" }),
      buildSession({ date: "2026-02-01" }),
      buildSession({ date: "2026-03-01" }),
    ];
    const all = [...deriveStrengths(sessions), ...deriveDevelopmentAreas(sessions)];
    expect(all.some((o) => o.key.startsWith("ground_contacts"))).toBe(false);
    expect(all.some((o) => o.key.startsWith("duty_factor"))).toBe(false);
    expect(all.some((o) => o.key.startsWith("flight_time"))).toBe(false);
  });
});

describe("generateEvolutionStatements", () => {
  it("empty for fewer than two sessions", () => {
    expect(generateEvolutionStatements([buildSession({ date: "2026-01-01" })])).toEqual([]);
  });

  it("produces a template-filled statement with the real percent change", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", cadence: 180 }),
      buildSession({ date: "2026-06-01", cadence: 190.8 }),
    ];
    const statements = generateEvolutionStatements(sessions);
    expect(statements.some((s) => s.includes("Cadence") && s.includes("6.0%"))).toBe(true);
  });
});

describe("computeTwinConfidence", () => {
  it("null when there are no completed sessions", () => {
    expect(computeTwinConfidence([])).toBeNull();
  });

  it("low confidence for a single, low-quality session", () => {
    const confidence = computeTwinConfidence([
      buildSession({ date: "2026-01-01", readiness: 40, detectionRate: 40, biomechanicsSkipped: true }),
    ]);
    expect(confidence).not.toBeNull();
    expect(confidence!.level).toBe("low");
  });

  it("a single session can never reach high confidence, no matter how good the quality", () => {
    // sessionCountScore alone caps at 8/40 for n=1, so even a perfect
    // recording (25+20+15=60 from the other three factors) tops out at
    // 68/100 - below the 75 "high" threshold. This is a documented
    // property of the formula (§12 of the architecture proposal), not
    // an incidental test value.
    const confidence = computeTwinConfidence([
      buildSession({ date: "2026-01-01", readiness: 100, detectionRate: 100, biomechanicsSkipped: false }),
    ]);
    expect(confidence!.level).not.toBe("high");
  });

  it("higher confidence accrues with more sessions and better quality", () => {
    const sessions = Array.from({ length: 6 }, (_, i) =>
      buildSession({ date: `2026-0${i + 1}-01`, readiness: 95, detectionRate: 98 }),
    );
    const confidence = computeTwinConfidence(sessions);
    expect(confidence!.level).toBe("high");
    expect(confidence!.sessionCount).toBe(6);
  });
});

describe("computeConsistency", () => {
  it("reports sampleSize 0 for no data", () => {
    const consistency = computeConsistency([]);
    expect(consistency.sampleSize).toBe(0);
    expect(consistency.uploadFrequencyDays).toBeNull();
  });

  it("computes a real upload frequency and completion rate across sessions", () => {
    const sessions = [
      buildSession({ date: "2026-01-01" }),
      buildSession({ date: "2026-01-11" }),
      buildSession({ date: "2026-01-21" }),
    ];
    const consistency = computeConsistency(sessions);
    expect(consistency.uploadFrequencyDays).toBe(10);
    expect(consistency.sessionCompletionRatePercent).toBe(100);
  });
});

describe("deriveDevelopmentStage", () => {
  it("maps session counts to the documented stage labels", () => {
    expect(deriveDevelopmentStage([]).label).toBe("No Twin Yet");
    expect(deriveDevelopmentStage([buildSession({ date: "2026-01-01" })]).label).toBe(
      "Just Starting",
    );
    expect(
      deriveDevelopmentStage([
        buildSession({ date: "2026-01-01" }),
        buildSession({ date: "2026-02-01" }),
      ]).label,
    ).toBe("Building a Baseline");
    expect(
      deriveDevelopmentStage(
        Array.from({ length: 5 }, (_, i) => buildSession({ date: `2026-0${i + 1}-01` })),
      ).label,
    ).toBe("Established Profile");
  });
});

describe("dominantEventName", () => {
  it("null for no completed sessions", () => {
    expect(dominantEventName([])).toBeNull();
  });

  it("picks the most common event among completed sessions", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", event: "Sprint" }),
      buildSession({ date: "2026-02-01", event: "Sprint" }),
      buildSession({ date: "2026-03-01", event: "Hurdles" }),
    ];
    expect(dominantEventName(sessions)).toBe("Sprint");
  });
});

// =========================================================================
// §28 verification: rigorous multi-sample hardening against mixed real-
// world analysis states. See docs/ENGINEERING_HANDOFF.md §28 for the full
// real-data verification this complements.
// =========================================================================

describe("exact mixed-state combinations (§28 verification)", () => {
  it("one completed + one skipped -> biomechanics metric sees 1 sample, recording-quality metric sees 2", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", biomechanicsSkipped: false, cadence: 180, readiness: 70 }),
      buildSession({ date: "2026-02-01", biomechanicsSkipped: true, readiness: 75 }),
    ];
    const cadenceMetric = METRIC_REGISTRY.find((m) => m.key === "cadence")!;
    const readinessMetric = METRIC_REGISTRY.find((m) => m.key === "readiness_score")!;

    const cadenceTrend = buildTwinMetricTrend(sessions, cadenceMetric);
    expect(cadenceTrend.trend.samples).toBe(1);
    expect(cadenceTrend.trend.direction).toBe("insufficient_data");

    const readinessTrend = buildTwinMetricTrend(sessions, readinessMetric);
    expect(readinessTrend.trend.samples).toBe(2);
  });

  it("an explicit null metric value is treated as missing, not zero", () => {
    const cadenceMetric = METRIC_REGISTRY.find((m) => m.key === "cadence")!;
    const sessions = [
      buildSession({ date: "2026-01-01", cadenceExplicitNull: true }),
      buildSession({ date: "2026-02-01", cadence: 180 }),
      buildSession({ date: "2026-03-01", cadence: 190 }),
    ];
    const { trend, points } = buildTwinMetricTrend(sessions, cadenceMetric);
    expect(trend.samples).toBe(2); // the explicit-null session is excluded, not counted as 0
    expect(points.some((p) => p.value === 0)).toBe(false);
  });

  it("a low-coverage joint angle is excluded from the trend, not treated as a valid low reading", () => {
    const leftKneeMetric = METRIC_REGISTRY.find((m) => m.key === "joint_angle_left_knee")!;
    const sessions = [
      buildSession({ date: "2026-01-01", leftKneeCoveragePercent: 30 }), // below the 60% threshold
      buildSession({ date: "2026-02-01", leftKneeCoveragePercent: 80 }),
      buildSession({ date: "2026-03-01", leftKneeCoveragePercent: 85 }),
    ];
    const { trend } = buildTwinMetricTrend(sessions, leftKneeMetric);
    expect(trend.samples).toBe(2); // the low-coverage session is excluded

    const trace = traceMetricInclusion(sessions, leftKneeMetric);
    expect(trace[0].included).toBe(false);
    expect(trace[0].reason).toMatch(/coverage/i);
  });
});

describe("recording quality is never conflated with athletic performance (§28 verification)", () => {
  it("improved recording readiness does not create an athletic-performance strength or evolution statement", () => {
    // readiness [70,75,80] keeps CV at ~5.4% (well under the 15%
    // high_variability threshold) while still trending clearly upward -
    // deliberately not a wider spread like [50,60,75] (CV ~16.7%), which
    // would get reclassified to "high_variability" and mask the
    // improving/regressing direction this test is actually about.
    const sessions = [
      buildSession({ date: "2026-01-01", cadence: 180, readiness: 70 }),
      buildSession({ date: "2026-02-01", cadence: 180, readiness: 75 }),
      buildSession({ date: "2026-03-01", cadence: 180, readiness: 80 }),
    ];

    const cadenceTrend = buildTwinMetricTrend(sessions, METRIC_REGISTRY.find((m) => m.key === "cadence")!);
    expect(cadenceTrend.trend.direction).toBe("stable"); // flat cadence, never "improving"

    const strengths = deriveStrengths(sessions);
    const cadenceStrength = strengths.find((s) => s.key.startsWith("cadence"));
    if (cadenceStrength) {
      expect(cadenceStrength.key).not.toContain("improving");
      expect(cadenceStrength.category).toBe("biomechanics");
    }

    const readinessStrength = strengths.find((s) => s.key.startsWith("readiness_score"));
    expect(readinessStrength?.category).toBe("recording_quality");

    const evolution = generateEvolutionStatements(sessions);
    expect(evolution.some((s) => s.includes("Cadence"))).toBe(false); // flat metric -> no evolution line
    expect(evolution.some((s) => s.includes("Recording Readiness Score"))).toBe(true);
  });

  it("athletic improvement is preserved as a strength even when recording quality declines in the same window", () => {
    // Same CV-safety reasoning as the previous test: readiness
    // [85,75,65] (CV ~10.9%) trends down clearly without tripping
    // high_variability, unlike a wider spread like [90,75,60] (CV ~16.3%).
    const sessions = [
      buildSession({ date: "2026-01-01", cadence: 170, readiness: 85 }),
      buildSession({ date: "2026-02-01", cadence: 180, readiness: 75 }),
      buildSession({ date: "2026-03-01", cadence: 190, readiness: 65 }),
    ];

    const strengths = deriveStrengths(sessions);
    const developmentAreas = deriveDevelopmentAreas(sessions);

    const cadenceStrength = strengths.find((s) => s.key === "cadence-improving");
    expect(cadenceStrength).toBeDefined();
    expect(cadenceStrength?.category).toBe("biomechanics");

    const readinessDevArea = developmentAreas.find((a) => a.key === "readiness_score-regressing");
    expect(readinessDevArea).toBeDefined();
    expect(readinessDevArea?.category).toBe("recording_quality");

    // Neither list conflates the two - the athletic strength doesn't leak
    // into development areas, and the quality regression doesn't leak
    // into strengths.
    expect(strengths.some((s) => s.key.startsWith("readiness_score"))).toBe(false);
    expect(developmentAreas.some((a) => a.key.startsWith("cadence"))).toBe(false);
  });
});

describe("incompatible analysis versions are excluded across every multi-session computation (§28 verification)", () => {
  it("buildTwinPersonalBests never selects a value from the minority-provider session", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", provider: "rtmpose", cadence: 170 }),
      buildSession({ date: "2026-02-01", provider: "rtmpose", cadence: 180 }),
      buildSession({ date: "2026-03-01", provider: "rtmpose", cadence: 185 }),
      buildSession({ date: "2026-04-01", provider: "mediapipe", cadence: 999 }), // would win if not excluded
    ];
    const pbs = buildTwinPersonalBests(sessions);
    const cadencePb = pbs.find((pb) => pb.metricKey === "cadence");
    expect(cadencePb?.value).toBe(185);
    expect(cadencePb?.value).not.toBe(999);
  });

  it("computeConsistency's sampleSize reflects only the dominant-provider group", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", provider: "rtmpose" }),
      buildSession({ date: "2026-02-01", provider: "rtmpose" }),
      buildSession({ date: "2026-03-01", provider: "rtmpose" }),
      buildSession({ date: "2026-04-01", provider: "mediapipe" }),
    ];
    const consistency = computeConsistency(sessions);
    expect(consistency.sampleSize).toBe(3);
  });

  it("computeTwinConfidence's sessionCount excludes the minority-provider session (a real bug fixed during §28 hardening)", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", provider: "rtmpose" }),
      buildSession({ date: "2026-02-01", provider: "rtmpose" }),
      buildSession({ date: "2026-03-01", provider: "rtmpose" }),
      buildSession({ date: "2026-04-01", provider: "mediapipe" }),
    ];
    const confidence = computeTwinConfidence(sessions);
    expect(confidence?.sessionCount).toBe(3); // not 4
  });

  it("deriveDevelopmentAreas' biomechanics-availability ratio excludes the minority-provider session", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", provider: "rtmpose", biomechanicsSkipped: true }),
      buildSession({ date: "2026-02-01", provider: "rtmpose", biomechanicsSkipped: true }),
      buildSession({ date: "2026-03-01", provider: "rtmpose", biomechanicsSkipped: true }),
      // If this minority session were wrongly included, the ratio would
      // be computed over 4 sessions instead of 3.
      buildSession({ date: "2026-04-01", provider: "mediapipe", biomechanicsSkipped: false }),
    ];
    const developmentAreas = deriveDevelopmentAreas(sessions);
    const biomechanicsArea = developmentAreas.find((a) => a.key === "biomechanics-availability");
    expect(biomechanicsArea?.detail).toContain("0 of 3");
  });

  it("traceMetricInclusion names the excluded minority-provider session and why", () => {
    const cadenceMetric = METRIC_REGISTRY.find((m) => m.key === "cadence")!;
    const sessions = [
      buildSession({ date: "2026-01-01", provider: "rtmpose" }),
      buildSession({ date: "2026-02-01", provider: "rtmpose" }),
      buildSession({ date: "2026-03-01", provider: "mediapipe" }),
    ];
    const trace = traceMetricInclusion(sessions, cadenceMetric);
    const minority = trace.find((t) => t.performanceId === sessions[2].id);
    expect(minority?.included).toBe(false);
    expect(minority?.reason).toMatch(/different pipeline/i);
  });
});

describe("experimental metrics never influence consistency's metric-stability average (§28 verification)", () => {
  it("wildly varying ground-contact/duty-factor/flight-time values do not inflate metricStabilityCvPercent", () => {
    function rawSession(
      date: string,
      groundContacts: number,
      dutyFactor: number,
      flightTime: number,
    ): TwinSessionInput {
      idCounter += 1;
      return {
        id: `perf-${idCounter}`,
        performanceNumber: idCounter,
        performanceDate: date,
        createdAt: date,
        events: [{ name: "Sprint", category: "Athletics" }],
        uploadStatus: "completed",
        analysisResult: {
          provider: "rtmpose",
          analysis: { detection_rate_percent: 95 },
          recording_quality: {
            rating: "Excellent",
            camera_view: { classification: "Side View" },
            analysis_readiness: { score: 85 },
            metrics: { full_body_visibility_score: 90, athlete_movement_score: 85 },
          },
          biomechanics: {
            status: "completed",
            segments: [
              {
                status: "completed",
                cadence: { steps_per_minute: 180 }, // held rock-stable
                stride: { stride_frequency_hz: 1.5 },
                knee_symmetry_score: 90, // held rock-stable
                ground_contact: { events: groundContacts }, // wildly varying, experimental
                duty_factor_percent: dutyFactor, // wildly varying, experimental
                flight_time: { median_flight_time_ms: flightTime }, // wildly varying, experimental
                joint_angles: {
                  left_knee: { mean_degrees: 150, coverage_percent: 80 },
                  right_knee: { mean_degrees: 148, coverage_percent: 82 },
                },
              },
            ],
          },
        },
      };
    }

    const sessions = [
      rawSession("2026-01-01", 10, 5, 50),
      rawSession("2026-02-01", 90, 45, 500),
      rawSession("2026-03-01", 20, 10, 100),
    ];

    const consistency = computeConsistency(sessions);
    // cadence and knee symmetry are perfectly constant across all three
    // sessions - if only production biomechanics metrics feed the
    // average, CV is exactly 0. Any leakage from the wildly-varying
    // experimental metrics would push this well above 0.
    expect(consistency.metricStabilityCvPercent).toBe(0);
  });
});

describe("output is stable regardless of input row order (§28 verification)", () => {
  it("buildTwinMetricTrend produces identical output for chronological, reversed, and shuffled input order", () => {
    const cadenceMetric = METRIC_REGISTRY.find((m) => m.key === "cadence")!;
    const chronological = [
      buildSession({ date: "2026-01-01", cadence: 170 }),
      buildSession({ date: "2026-02-01", cadence: 180 }),
      buildSession({ date: "2026-03-01", cadence: 190 }),
      buildSession({ date: "2026-04-01", cadence: 185 }),
    ];
    const reversed = [...chronological].reverse();
    const shuffled = [chronological[2], chronological[0], chronological[3], chronological[1]];

    const a = buildTwinMetricTrend(chronological, cadenceMetric);
    const b = buildTwinMetricTrend(reversed, cadenceMetric);
    const c = buildTwinMetricTrend(shuffled, cadenceMetric);

    expect(b.trend).toEqual(a.trend);
    expect(c.trend).toEqual(a.trend);
    expect(b.points).toEqual(a.points);
    expect(c.points).toEqual(a.points);
  });

  it("buildTwinPersonalBests and computeConsistency are also order-invariant", () => {
    const chronological = [
      buildSession({ date: "2026-01-01", cadence: 170, readiness: 60 }),
      buildSession({ date: "2026-02-01", cadence: 195, readiness: 70 }),
      buildSession({ date: "2026-03-01", cadence: 180, readiness: 80 }),
    ];
    const shuffled = [chronological[1], chronological[2], chronological[0]];

    expect(buildTwinPersonalBests(shuffled)).toEqual(buildTwinPersonalBests(chronological));
    expect(computeConsistency(shuffled)).toEqual(computeConsistency(chronological));
  });

  it("deriveStrengths, deriveDevelopmentAreas, and generateEvolutionStatements are order-invariant", () => {
    const chronological = [
      buildSession({ date: "2026-01-01", cadence: 170, readiness: 90 }),
      buildSession({ date: "2026-02-01", cadence: 180, readiness: 75 }),
      buildSession({ date: "2026-03-01", cadence: 190, readiness: 60 }),
    ];
    const shuffled = [chronological[2], chronological[0], chronological[1]];

    expect(deriveStrengths(shuffled)).toEqual(deriveStrengths(chronological));
    expect(deriveDevelopmentAreas(shuffled)).toEqual(deriveDevelopmentAreas(chronological));
    expect(generateEvolutionStatements(shuffled)).toEqual(generateEvolutionStatements(chronological));
  });

  it("an exact count tie between two provider groups picks the same dominant provider regardless of input order (regression - a real bug found and fixed during §28 hardening)", () => {
    // Before the fix, groupByDominantProvider broke count ties by
    // whichever provider was iterated first - i.e. whichever session
    // came first in the input array - so feeding the exact same two
    // sessions in a different order could flip which provider "won."
    // Live-verified against the real QA account during §28: with one
    // real rtmpose session and one (temporarily, clearly-marked) session
    // simulating a different pipeline, the tie flipped based on fetch
    // order alone before this fix. Now broken by each group's latest
    // session date - a property of the data, not its position.
    const rtmposeSession = buildSession({ date: "2026-01-01", provider: "rtmpose", cadence: 170 });
    const mediapipeSession = buildSession({ date: "2026-02-01", provider: "mediapipe", cadence: 999 });

    const orderA = groupByDominantProvider([rtmposeSession, mediapipeSession]);
    const orderB = groupByDominantProvider([mediapipeSession, rtmposeSession]);

    expect(orderA.dominantProvider).toBe(orderB.dominantProvider);
    // The later session (mediapipe, 2026-02-01) should win the tie in
    // both orderings - not whichever happened to be iterated first.
    expect(orderA.dominantProvider).toBe("mediapipe");
    expect(orderB.dominantProvider).toBe("mediapipe");
  });

  it("same-date sessions resolve deterministically for a given input order - a disclosed limitation, not silent corruption", () => {
    // Two sessions sharing an identical date: JS's stable sort (spec
    // since ES2019) means date ties preserve whichever relative order
    // they arrived in. Both the athlete and coach queries order by
    // created_at descending identically (performance.service.ts /
    // connections.service.ts), so in practice this resolves the same
    // way for both views - this test documents that resolution is
    // deterministic for a given input order, not that a same-day tie has
    // one single "correct" winner (there isn't one - see §28 of
    // docs/ENGINEERING_HANDOFF.md).
    const sameDayA = buildSession({ date: "2026-01-01", cadence: 170 });
    const sameDayB = buildSession({ date: "2026-01-01", cadence: 200 });
    const other = buildSession({ date: "2026-02-01", cadence: 180 });

    const orderX = [sameDayA, sameDayB, other];
    const orderY = [sameDayB, sameDayA, other];

    const cadenceMetric = METRIC_REGISTRY.find((m) => m.key === "cadence")!;
    const trendX = buildTwinMetricTrend(orderX, cadenceMetric);
    const trendY = buildTwinMetricTrend(orderY, cadenceMetric);

    expect(trendX.trend.samples).toBe(3);
    expect(trendY.trend.samples).toBe(3);
  });
});

describe("rounding and percent-change consistency across consumers (§28 verification)", () => {
  it("percentChange is exact, and every consumer that displays it rounds identically to 1 decimal", () => {
    const twoPoint = analyzeTrend("cadence", [180, 190.8]);
    expect(twoPoint.percentChange).toBeCloseTo(6.0, 5);

    const sessions = [
      buildSession({ date: "2026-01-01", cadence: 180 }),
      buildSession({ date: "2026-06-01", cadence: 190.8 }),
      buildSession({ date: "2026-09-01", cadence: 195 }),
    ];
    const strengths = deriveStrengths(sessions);
    const evolution = generateEvolutionStatements(sessions);
    const cadenceStrength = strengths.find((s) => s.key === "cadence-improving");
    const cadenceEvolution = evolution.find((s) => s.includes("Cadence"));

    const pctInStrength = cadenceStrength?.detail.match(/([\d.]+)%/)?.[1];
    const pctInEvolution = cadenceEvolution?.match(/([\d.]+)%/)?.[1];
    expect(pctInStrength).toBeDefined();
    expect(pctInStrength).toBe(pctInEvolution);
  });
});

describe("no NaN/Infinity in trend or consistency output for degenerate inputs (§28 verification)", () => {
  it("all-zero metric values do not produce NaN or Infinity anywhere", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", cadence: 0 }),
      buildSession({ date: "2026-02-01", cadence: 0 }),
      buildSession({ date: "2026-03-01", cadence: 0 }),
    ];
    const cadenceMetric = METRIC_REGISTRY.find((m) => m.key === "cadence")!;
    const { trend } = buildTwinMetricTrend(sessions, cadenceMetric);

    expect(Number.isNaN(trend.slopePerSession)).toBe(false);
    expect(Number.isFinite(trend.slopePerSession!)).toBe(true);
    expect(trend.percentChange).toBeNull(); // firstValue is 0 - undefined, not Infinity
    expect(trend.coefficientOfVariationPercent).toBeNull(); // mean is 0 - undefined, not NaN
    expect(trend.direction).toBe("stable");
  });

  it("a value dropping to zero produces a bounded percent change, never Infinity", () => {
    const trend = analyzeTrend("cadence", [1, 0]);
    expect(trend.percentChange).not.toBeNull();
    expect(Number.isFinite(trend.percentChange!)).toBe(true);
    expect(trend.percentChange).toBeCloseTo(-100, 5);
  });

  it("computeConsistency never divides by zero when every value is identical", () => {
    const sessions = [
      buildSession({ date: "2026-01-01", readiness: 80, cadence: 180 }),
      buildSession({ date: "2026-02-01", readiness: 80, cadence: 180 }),
      buildSession({ date: "2026-03-01", readiness: 80, cadence: 180 }),
    ];
    const consistency = computeConsistency(sessions);
    expect(consistency.recordingConsistencyCvPercent).toBe(0);
    expect(Number.isNaN(consistency.recordingConsistencyCvPercent!)).toBe(false);
  });
});

describe("stable/plateau boundary classification (§28 verification)", () => {
  it("a change exactly at the practical threshold classifies as stable; just outside classifies as improving", () => {
    // practicalThreshold = max(abs(average) * 0.0025, 1e-9). For an
    // average of 200, that's 0.5 - a 2-point slope equals (latest -
    // first) exactly, so this pins the stable/improving boundary precisely.
    const atThreshold = analyzeTrend("cadence", [199.75, 200.25]); // slope = 0.5, average = 200
    expect(atThreshold.direction).toBe("stable");

    const justOverThreshold = analyzeTrend("cadence", [199.7, 200.3]); // slope = 0.6, average = 200
    expect(justOverThreshold.direction).toBe("improving");
  });
});

describe("Personal Best source-link correctness (§28 verification)", () => {
  it("every personal best carries the exact performanceId and recordedAt of its originating session", () => {
    const s1 = buildSession({ date: "2026-01-01", cadence: 170, readiness: 60 });
    const s2 = buildSession({ date: "2026-02-01", cadence: 195, readiness: 95 }); // best cadence AND best readiness
    const s3 = buildSession({ date: "2026-03-01", cadence: 180, readiness: 70 });
    const sessions = [s1, s2, s3];

    const pbs = buildTwinPersonalBests(sessions);
    const cadencePb = pbs.find((pb) => pb.metricKey === "cadence")!;
    const readinessPb = pbs.find((pb) => pb.metricKey === "readiness_score")!;

    expect(cadencePb.performanceId).toBe(s2.id);
    expect(cadencePb.recordedAt).toBe(s2.performanceDate);
    expect(readinessPb.performanceId).toBe(s2.id);
    expect(readinessPb.recordedAt).toBe(s2.performanceDate);
  });
});

describe("traceMetricInclusion (§28 verification, debug/test-only helper)", () => {
  it("explains every inclusion/exclusion reason for a mixed dataset", () => {
    const cadenceMetric = METRIC_REGISTRY.find((m) => m.key === "cadence")!;
    const completedGood = buildSession({ date: "2026-01-01", cadence: 180 });
    const skipped = buildSession({ date: "2026-02-01", biomechanicsSkipped: true });
    const failedUpload = buildSession({ date: "2026-03-01", uploadStatus: "failed", cadence: 175 });
    const wrongProvider = buildSession({ date: "2026-04-01", provider: "mediapipe", cadence: 185 });

    const sessions = [completedGood, skipped, failedUpload, wrongProvider];
    const trace = traceMetricInclusion(sessions, cadenceMetric);

    expect(trace.find((t) => t.performanceId === completedGood.id)?.included).toBe(true);
    expect(trace.find((t) => t.performanceId === skipped.id)?.included).toBe(false);
    expect(trace.find((t) => t.performanceId === failedUpload.id)?.included).toBe(false);
    expect(trace.find((t) => t.performanceId === wrongProvider.id)?.included).toBe(false);

    expect(trace.find((t) => t.performanceId === skipped.id)?.reason).toMatch(/no value/i);
    expect(trace.find((t) => t.performanceId === failedUpload.id)?.reason).toMatch(/upload_status/i);
    expect(trace.find((t) => t.performanceId === wrongProvider.id)?.reason).toMatch(/different pipeline/i);
  });
});
