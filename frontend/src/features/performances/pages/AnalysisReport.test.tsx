import { describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";

import { AnalysisReport } from "./PerformanceDetail";
import {
  completedWithBiomechanicsFixture,
  completedWithMissingValuesFixture,
  skippedBiomechanicsFixture,
} from "../__fixtures__/analysisResult.fixture";

describe("AnalysisReport", () => {
  it("renders the skipped-biomechanics reason instead of a report", () => {
    render(<AnalysisReport result={skippedBiomechanicsFixture} />);

    expect(
      screen.getByText(/biomechanics analysis was skipped/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/not ready for analysis/i)).toBeInTheDocument();
  });

  it("renders recording quality warnings and recommendations together", () => {
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

  it("renders per-segment limitations", () => {
    render(<AnalysisReport result={completedWithBiomechanicsFixture} />);

    expect(
      screen.getByText(/angles remain projected 2d image-plane/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/not laboratory or force-plate validated/i),
    ).toBeInTheDocument();
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
