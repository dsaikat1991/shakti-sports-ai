import { describe, expect, it } from "vitest";

import {
  METRIC_REGISTRY,
  defineMetric,
  deriveDefaultTrendMode,
  supportsObjectiveComparison,
  validateMetricRegistry,
  type ComparisonMode,
  type ExtractedMetric,
} from "./metricRegistry";

const VALID_COMPARISON_MODES: ComparisonMode[] = [
  "HIGHER_IS_BETTER",
  "LOWER_IS_BETTER",
  "TARGET_RANGE",
  "SYMMETRY",
  "NEUTRAL",
  "EXPERIMENTAL",
  "NOT_COMPARABLE",
];

const JOINT_ANGLE_KEYS = [
  "joint_angle_left_knee",
  "joint_angle_right_knee",
  "joint_angle_left_hip",
  "joint_angle_right_hip",
  "joint_angle_left_elbow",
  "joint_angle_right_elbow",
];

function stubAccessor(): ExtractedMetric | null {
  return { value: 1 };
}

describe("METRIC_REGISTRY structural integrity", () => {
  it("does not run any validation automatically on import", () => {
    // If importing this module had a side effect that threw, every other
    // test file importing METRIC_REGISTRY would already have failed
    // before this test ran - asserted explicitly rather than left
    // implicit (docs/ENGINEERING_HANDOFF.md §33).
    expect(() => METRIC_REGISTRY).not.toThrow();
    expect(METRIC_REGISTRY.length).toBeGreaterThan(0);
  });

  it("has no validation violations", () => {
    expect(validateMetricRegistry(METRIC_REGISTRY)).toEqual([]);
  });

  it("has unique metric keys", () => {
    const keys = METRIC_REGISTRY.map((m) => m.key);
    expect(new Set(keys).size).toBe(keys.length);
  });

  it("every metric has required metadata populated", () => {
    for (const metric of METRIC_REGISTRY) {
      expect(metric.key, metric.key).toBeTruthy();
      expect(metric.label, metric.key).toBeTruthy();
      expect(metric.unit, metric.key).toBeTruthy();
      expect(["recording_quality", "biomechanics"], metric.key).toContain(metric.category);
      expect(metric.applicableEvents.length, metric.key).toBeGreaterThan(0);
      expect(metric.backendSource, metric.key).toBeTruthy();
      expect(metric.analysisResultPath, metric.key).toBeTruthy();
      expect(typeof metric.accessor, metric.key).toBe("function");
      expect(typeof metric.format, metric.key).toBe("function");
      expect(["FIRST_SEGMENT", "SESSION_LEVEL"], metric.key).toContain(metric.aggregationMethod);
    }
  });

  it("every comparisonMode is a valid enum value", () => {
    for (const metric of METRIC_REGISTRY) {
      expect(VALID_COMPARISON_MODES, metric.key).toContain(metric.comparisonMode);
    }
  });

  it("experimental mirrors status === 'experimental' for every metric", () => {
    for (const metric of METRIC_REGISTRY) {
      expect(metric.experimental, metric.key).toBe(metric.status === "experimental");
    }
  });

  it("every experimental-status metric uses comparisonMode EXPERIMENTAL", () => {
    for (const metric of METRIC_REGISTRY) {
      if (metric.status === "experimental") {
        expect(metric.comparisonMode, metric.key).toBe("EXPERIMENTAL");
      }
    }
  });

  it("every hidden metric has supportsTwin and supportsCoachComparison both false", () => {
    const hiddenMetrics = METRIC_REGISTRY.filter((m) => m.hidden);
    expect(hiddenMetrics.length).toBeGreaterThan(0); // sanity: the 10 inventory entries exist
    for (const metric of hiddenMetrics) {
      expect(metric.supportsTwin, metric.key).toBe(false);
      expect(metric.supportsCoachComparison, metric.key).toBe(false);
    }
  });

  it("every metric's trendMode matches deriveDefaultTrendMode(comparisonMode), since no current entry overrides it", () => {
    for (const metric of METRIC_REGISTRY) {
      expect(metric.trendMode, metric.key).toBe(deriveDefaultTrendMode(metric.comparisonMode));
    }
  });

  it("cadence and stride_frequency remain HIGHER_IS_BETTER with disclosed limitation text", () => {
    const cadence = METRIC_REGISTRY.find((m) => m.key === "cadence");
    const strideFrequency = METRIC_REGISTRY.find((m) => m.key === "stride_frequency");
    expect(cadence?.comparisonMode).toBe("HIGHER_IS_BETTER");
    expect(strideFrequency?.comparisonMode).toBe("HIGHER_IS_BETTER");
    expect(cadence?.limitationText).toBeTruthy();
    expect(strideFrequency?.limitationText).toBeTruthy();
  });

  it("all six joint-angle metrics remain NEUTRAL", () => {
    for (const key of JOINT_ANGLE_KEYS) {
      const metric = METRIC_REGISTRY.find((m) => m.key === key);
      expect(metric?.comparisonMode, key).toBe("NEUTRAL");
    }
  });
});

describe("supportsObjectiveComparison", () => {
  it("is true only for HIGHER_IS_BETTER, LOWER_IS_BETTER, SYMMETRY", () => {
    expect(supportsObjectiveComparison("HIGHER_IS_BETTER")).toBe(true);
    expect(supportsObjectiveComparison("LOWER_IS_BETTER")).toBe(true);
    expect(supportsObjectiveComparison("SYMMETRY")).toBe(true);
    expect(supportsObjectiveComparison("NEUTRAL")).toBe(false);
    expect(supportsObjectiveComparison("EXPERIMENTAL")).toBe(false);
    expect(supportsObjectiveComparison("TARGET_RANGE")).toBe(false);
    expect(supportsObjectiveComparison("NOT_COMPARABLE")).toBe(false);
  });
});

describe("validateMetricRegistry", () => {
  it("returns no violations for an empty registry", () => {
    expect(validateMetricRegistry([])).toEqual([]);
  });

  it("flags a duplicate key", () => {
    const base = METRIC_REGISTRY[0];
    const violations = validateMetricRegistry([base, base]);
    expect(violations.some((v) => v.message.includes("Duplicate"))).toBe(true);
  });

  it("flags an experimental metric with a non-EXPERIMENTAL comparisonMode, as data rather than a thrown error", () => {
    // Constructed as a plain object (not via defineMetric) to simulate a
    // malformed future entry - proves violations are caught without
    // relying on defineMetric's own construction-time behavior.
    const malformed = {
      ...METRIC_REGISTRY[0],
      key: "malformed-test-metric",
      status: "experimental" as const,
      comparisonMode: "HIGHER_IS_BETTER" as const,
    };
    expect(() => validateMetricRegistry([malformed])).not.toThrow();
    const violations = validateMetricRegistry([malformed]);
    expect(violations.some((v) => v.key === "malformed-test-metric")).toBe(true);
  });
});

describe("defineMetric override support", () => {
  const baseInput = {
    key: "synthetic-metric",
    label: "Synthetic Metric",
    unit: "unit",
    category: "recording_quality" as const,
    applicableEvents: ["Sprint"],
    status: "production" as const,
    accessor: stubAccessor,
    format: (m: ExtractedMetric) => `${m.value}`,
    backendSource: "test-fixture",
    analysisResultPath: "test.fixture.path",
    comparisonMode: "HIGHER_IS_BETTER" as const,
    aggregationMethod: "SESSION_LEVEL" as const,
  };

  it("derives trendMode by default", () => {
    expect(defineMetric(baseInput).trendMode).toBe("INCREASING");
  });

  it("allows an explicit trendMode override", () => {
    expect(defineMetric({ ...baseInput, trendMode: "MAINTAIN" }).trendMode).toBe("MAINTAIN");
  });

  it("derives supportsRanking by default (true for a HIGHER_IS_BETTER production metric)", () => {
    expect(defineMetric(baseInput).supportsRanking).toBe(true);
  });

  it("allows an explicit supportsRanking override", () => {
    expect(defineMetric({ ...baseInput, supportsRanking: false }).supportsRanking).toBe(false);
  });

  it("derives supportsTwin/supportsCoachComparison as true by default", () => {
    const metric = defineMetric(baseInput);
    expect(metric.supportsTwin).toBe(true);
    expect(metric.supportsCoachComparison).toBe(true);
  });

  it("allows explicit supportsTwin/supportsCoachComparison overrides", () => {
    const metric = defineMetric({ ...baseInput, supportsTwin: false, supportsCoachComparison: false });
    expect(metric.supportsTwin).toBe(false);
    expect(metric.supportsCoachComparison).toBe(false);
  });

  it("never throws at construction time, even for a malformed experimental entry", () => {
    // The critical safety property from the architecture review: importing
    // metricRegistry.ts (or constructing an entry) must never crash the
    // app in production. Malformed entries are reportable via
    // validateMetricRegistry (see above), not fatal at construction.
    expect(() =>
      defineMetric({ ...baseInput, status: "experimental", comparisonMode: "HIGHER_IS_BETTER" }),
    ).not.toThrow();
  });
});
