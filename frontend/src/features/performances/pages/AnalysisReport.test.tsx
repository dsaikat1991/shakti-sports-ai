import { describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";

import {
  AnalysisReport,
  buildGatingChecks,
  buildQualityChecks,
  diagnoseSkipReason,
} from "./PerformanceDetail";
import {
  completedWithBiomechanicsFixture,
  completedWithMissingValuesFixture,
  skippedBiomechanicsFixture,
  skippedFullBodyNotVisibleFixture,
} from "../__fixtures__/analysisResult.fixture";

describe("AnalysisReport", () => {
  it("renders a specific, actionable reason instead of the generic backend rating string", () => {
    render(<AnalysisReport result={skippedBiomechanicsFixture} />);

    expect(
      screen.getByText(/biomechanics analysis could not be completed/i),
    ).toBeInTheDocument();
    // Not just the raw backend "reason" (Not Ready for Analysis) - the
    // specific failing measurement.
    expect(
      screen.getByText(/feet were visible in only 44% of analysed frames/i),
    ).toBeInTheDocument();
  });

  it("renders the full readiness-check breakdown table with pass/fail badges", () => {
    render(<AnalysisReport result={skippedBiomechanicsFixture} />);

    expect(screen.getByText("Biomechanics Readiness Checks")).toBeInTheDocument();
    expect(screen.getByText("Feet visibility")).toBeInTheDocument();
    expect(screen.getByText("44%")).toBeInTheDocument();

    const feetRow = screen.getByText("Feet visibility").closest("tr");
    expect(within(feetRow as HTMLElement).getByText("Failed")).toBeInTheDocument();

    const hipsRow = screen.getByText("Hips visibility").closest("tr");
    expect(within(hipsRow as HTMLElement).getByText("Passed")).toBeInTheDocument();
  });

  it("renders general (non-gating) quality checks separately from the hard gates", () => {
    render(<AnalysisReport result={skippedBiomechanicsFixture} />);

    expect(screen.getByText("General Recording Quality")).toBeInTheDocument();
    expect(screen.getByText("Lighting")).toBeInTheDocument();
  });
});

describe("diagnoseSkipReason", () => {
  it("identifies the worst individual body-part failure (feet) even when the composite score passes", () => {
    // skippedBiomechanicsFixture: full_body_visibility_score is 82.56
    // (passes the >=75 composite gate) but feet (44.48%) and ankles
    // (67.76%) individually fail their own >=70% gate - the backend's
    // own rating text ("Not Ready for Analysis") misses this because it
    // only checks the composite, not each group.
    const reason = diagnoseSkipReason(
      skippedBiomechanicsFixture.recording_quality,
    );
    expect(reason).toContain("feet");
    expect(reason).toContain("44%");
    expect(reason).not.toContain("ankles"); // feet is strictly worse, headline picks one
  });

  it("identifies feet as the driver of a failing composite score", () => {
    // skippedFullBodyNotVisibleFixture: composite (74.33) fails its
    // >=75 gate, and feet (52.02%) is the only individual group that
    // also fails - matches the backend's own "Full Body Not Visible"
    // rating, but with the actual number instead of a generic label.
    const reason = diagnoseSkipReason(
      skippedFullBodyNotVisibleFixture.recording_quality,
    );
    expect(reason).toContain("feet");
    expect(reason).toContain("52%");
  });

  it("flags a non-side camera angle before checking any body-visibility numbers", () => {
    const reason = diagnoseSkipReason({
      camera_view: { classification: "Front View" },
      body_visibility: { feet: 10 }, // would otherwise dominate - angle must win
    });
    expect(reason).toMatch(/front rather than the side/i);
  });
});

describe("buildGatingChecks / buildQualityChecks", () => {
  it("marks camera height as an independent failing gate (#9's case)", () => {
    const checks = buildGatingChecks(
      skippedFullBodyNotVisibleFixture.recording_quality,
    );
    const cameraHeight = checks.find((c) => c.label === "Camera height");
    expect(cameraHeight).toMatchObject({ passed: false, value: "30/100" });
  });

  it("does not fabricate a required threshold for informational-only checks", () => {
    const checks = buildQualityChecks(
      skippedBiomechanicsFixture.recording_quality,
    );
    expect(checks.every((c) => c.required === undefined)).toBe(true);
  });
});

describe("AnalysisReport - completed report rendering", () => {
  it("renders recording quality warnings and recommendations in their own separate sections", () => {
    render(<AnalysisReport result={completedWithBiomechanicsFixture} />);

    expect(
      screen.getByText(/athlete appears too far from the camera/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/move the camera closer/i),
    ).toBeInTheDocument();
  });

  it("sorts joint angles into canonical order regardless of input key order", () => {
    // The fixture's joint_angles object is deliberately ordered the way
    // Postgres's jsonb column actually returns it (by key length, then
    // alphabetically): left_hip, left_knee, right_hip, left_elbow,
    // right_knee, right_elbow. The rendered table must not follow that -
    // it should always show left_knee, right_knee, left_hip, right_hip,
    // left_elbow, right_elbow.
    render(<AnalysisReport result={completedWithBiomechanicsFixture} />);

    const rows = screen.getAllByRole("row").slice(1); // drop header row
    const jointNames = rows.map(
      (row) => within(row).getAllByRole("cell")[0].textContent,
    );

    expect(jointNames).toEqual([
      "Left knee angle",
      "Right knee angle",
      "Left hip angle",
      "Right hip angle",
      "Left elbow angle",
      "Right elbow angle",
    ]);
  });

  it("rolls per-segment limitations up into one deduplicated, clearly-labeled section", () => {
    render(<AnalysisReport result={completedWithBiomechanicsFixture} />);

    expect(screen.getByText("Limitations")).toBeInTheDocument();
    expect(
      screen.getByText(/angles remain projected 2d image-plane/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/not laboratory or force-plate validated/i),
    ).toBeInTheDocument();
  });

  it("separates Recording Quality, AI Analysis, Biomechanics, Limitations and Recommendations into distinct labeled sections", () => {
    render(<AnalysisReport result={completedWithBiomechanicsFixture} />);

    expect(screen.getByText("AI Analysis")).toBeInTheDocument();
    // "Recording Quality" appears twice - the section heading and the
    // stat tile label inside it - both are expected.
    expect(screen.getAllByText("Recording Quality").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Biomechanics")).toBeInTheDocument();
    expect(screen.getByText("Limitations")).toBeInTheDocument();
    expect(screen.getByText("Recommendations")).toBeInTheDocument();
  });

  it("renders real segment metrics with correct units", () => {
    render(<AnalysisReport result={completedWithBiomechanicsFixture} />);

    expect(screen.getByText("188 steps/min")).toBeInTheDocument();
    expect(screen.getByText("1.56 Hz")).toBeInTheDocument();
    expect(screen.getByText("46 detected")).toBeInTheDocument();
    expect(screen.getByText("23.5%")).toBeInTheDocument();
    expect(screen.getByText("260 ms")).toBeInTheDocument();
    expect(screen.getByText("86%")).toBeInTheDocument();
  });

  it("falls back to N/A or a dash for missing/null values instead of crashing", () => {
    render(<AnalysisReport result={completedWithMissingValuesFixture} />);

    expect(screen.getByText("Cadence").nextSibling?.textContent).toBe("N/A");
    expect(screen.getByText("Duty Factor").nextSibling?.textContent).toBe(
      "N/A",
    );
    expect(screen.getByText("Knee Symmetry").nextSibling?.textContent).toBe(
      "N/A",
    );

    const row = screen.getAllByRole("row")[1];
    const cells = within(row).getAllByRole("cell");
    expect(cells.map((cell) => cell.textContent)).toEqual([
      "Left knee angle",
      "—",
      "—",
      "—",
      "—",
    ]);
  });
});
