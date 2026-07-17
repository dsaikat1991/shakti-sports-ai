import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { MetricSection } from "./PartnerCompare";
import { defineMetric, type ExtractedMetric, METRIC_REGISTRY } from "../../performances/lib/metricRegistry";
import type { AnalysisResult } from "../../performances/types/analysis";
import {
  completedWithBiomechanicsFixture,
  completedWithMissingValuesFixture,
} from "../../performances/__fixtures__/analysisResult.fixture";

// Deep-clones a real fixture and applies a small set of path overrides -
// every test below starts from a genuine, previously-captured live
// analysis_result (docs/ENGINEERING_HANDOFF.md §6) rather than inventing
// a shape from scratch, matching the existing AnalysisReport.test.tsx
// convention of testing against real fixture data.
function withOverrides(base: AnalysisResult, apply: (clone: any) => void): AnalysisResult {
  const clone = JSON.parse(JSON.stringify(base));
  apply(clone);
  return clone as AnalysisResult;
}

function greenClassOf(text: string): boolean {
  return screen.getByText(text).className.includes("text-green-700");
}

const detectionRateMetric = METRIC_REGISTRY.find((m) => m.key === "detection_rate")!;
const kneeSymmetryMetric = METRIC_REGISTRY.find((m) => m.key === "knee_symmetry")!;
const jointAngleMetric = METRIC_REGISTRY.find((m) => m.key === "joint_angle_left_knee")!;
const groundContactsMetric = METRIC_REGISTRY.find((m) => m.key === "ground_contacts")!;

// No LOWER_IS_BETTER metric exists in the real registry today (§33) - a
// synthetic one, built via the same defineMetric() every real entry uses,
// reading a real field (video.duration_seconds) is the only way to test
// this branch of winningSide() without adding a fabricated metric to the
// production registry.
const durationMetric = defineMetric({
  key: "test-duration",
  label: "Clip Duration",
  unit: "s",
  category: "recording_quality",
  applicableEvents: ["Sprint"],
  status: "production",
  comparisonMode: "LOWER_IS_BETTER",
  aggregationMethod: "SESSION_LEVEL",
  backendSource: "test-fixture",
  analysisResultPath: "video.duration_seconds",
  accessor: (result): ExtractedMetric | null => {
    const value = result.video?.duration_seconds;
    return typeof value === "number" ? { value } : null;
  },
  format: (m) => `${m.value.toFixed(2)}s`,
});

describe("MetricSection winner logic (docs/ENGINEERING_HANDOFF.md §33)", () => {
  it("HIGHER_IS_BETTER highlights only the larger value", () => {
    const resultA = completedWithBiomechanicsFixture; // detection_rate_percent: 100
    const resultB = withOverrides(resultA, (c) => {
      c.analysis.detection_rate_percent = 80;
    });

    render(
      <MetricSection
        title=""
        metrics={[detectionRateMetric]}
        resultA={resultA}
        resultB={resultB}
        eventName="Sprint"
      />,
    );

    expect(greenClassOf("100%")).toBe(true);
    expect(greenClassOf("80%")).toBe(false);
  });

  it("LOWER_IS_BETTER highlights only the smaller value", () => {
    const resultA = completedWithBiomechanicsFixture; // duration_seconds: 15.74
    const resultB = withOverrides(resultA, (c) => {
      c.video.duration_seconds = 25;
    });

    render(
      <MetricSection
        title=""
        metrics={[durationMetric]}
        resultA={resultA}
        resultB={resultB}
        eventName="Sprint"
      />,
    );

    expect(greenClassOf("15.74s")).toBe(true);
    expect(greenClassOf("25.00s")).toBe(false);
  });

  it("SYMMETRY highlights only the larger symmetry score", () => {
    const resultA = completedWithBiomechanicsFixture; // knee_symmetry_score: 85.98
    const resultB = withOverrides(resultA, (c) => {
      c.biomechanics.segments[0].knee_symmetry_score = 70;
    });

    render(
      <MetricSection
        title=""
        metrics={[kneeSymmetryMetric]}
        resultA={resultA}
        resultB={resultB}
        eventName="Sprint"
      />,
    );

    expect(greenClassOf("86%")).toBe(true);
    expect(greenClassOf("70%")).toBe(false);
  });

  it("NEUTRAL (joint angle) highlights neither side", () => {
    const resultA = completedWithBiomechanicsFixture; // left_knee mean_degrees: 146.71
    const resultB = withOverrides(resultA, (c) => {
      c.biomechanics.segments[0].joint_angles.left_knee.mean_degrees = 170;
    });

    render(
      <MetricSection
        title=""
        metrics={[jointAngleMetric]}
        resultA={resultA}
        resultB={resultB}
        eventName="Sprint"
      />,
    );

    expect(greenClassOf("147°")).toBe(false);
    expect(greenClassOf("170°")).toBe(false);
  });

  it("EXPERIMENTAL highlights neither side", () => {
    const resultA = completedWithBiomechanicsFixture; // ground_contact.events: 46
    const resultB = withOverrides(resultA, (c) => {
      c.biomechanics.segments[0].ground_contact.events = 30;
    });

    render(
      <MetricSection
        title=""
        metrics={[groundContactsMetric]}
        resultA={resultA}
        resultB={resultB}
        eventName="Sprint"
        experimental
      />,
    );

    expect(greenClassOf("46 detected")).toBe(false);
    expect(greenClassOf("30 detected")).toBe(false);
  });

  it("equal values highlight neither side", () => {
    const resultA = completedWithBiomechanicsFixture;
    const resultB = withOverrides(resultA, () => {
      /* no changes - both sides identical */
    });

    render(
      <MetricSection
        title=""
        metrics={[detectionRateMetric]}
        resultA={resultA}
        resultB={resultB}
        eventName="Sprint"
      />,
    );

    const matches = screen.getAllByText("100%");
    expect(matches).toHaveLength(2);
    for (const el of matches) {
      expect(el.className.includes("text-green-700")).toBe(false);
    }
  });

  it("missing values do not create a false winner", () => {
    const resultA = completedWithBiomechanicsFixture; // real knee_symmetry_score
    const resultB = completedWithMissingValuesFixture; // knee_symmetry_score: null

    render(
      <MetricSection
        title=""
        metrics={[kneeSymmetryMetric]}
        resultA={resultA}
        resultB={resultB}
        eventName="Sprint"
      />,
    );

    expect(screen.getByText(/not comparable/i)).toBeInTheDocument();
    expect(screen.queryByText("86%")).not.toBeInTheDocument();
  });
});
