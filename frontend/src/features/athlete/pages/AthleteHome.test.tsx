import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { deriveHomeHeroState, HeroCard } from "./AthleteHome";
import {
  completedWithBiomechanicsFixture,
  skippedFullBodyNotVisibleFixture,
} from "../../performances/__fixtures__/analysisResult.fixture";

vi.mock("../../auth/context/AuthContext", () => ({
  useAuth: () => ({ user: { id: "athlete-1", email: "priya@example.com" } }),
}));
vi.mock("../hooks/useAthleteDashboard", () => ({
  useAthleteDashboard: () => ({ data: [], isLoading: false, error: null }),
}));
vi.mock("../hooks/useAthleteProfile", () => ({
  useAthleteProfile: () => ({ data: null }),
}));
vi.mock("../hooks/useAthleteGoals", () => ({
  useAthleteGoals: () => ({ data: [] }),
}));
vi.mock("../hooks/useAthleteNotifications", () => ({
  useAthleteNotifications: () => ({ notifications: [] }),
}));

// Real fixtures (docs/ENGINEERING_HANDOFF.md §6), not invented shapes -
// matching the existing PartnerCompare.test.tsx / AnalysisReport.test.tsx
// convention. Each is wrapped in the minimal performance-row fields
// deriveHomeHeroState/HeroCard actually read.
function performance(overrides: Record<string, unknown>) {
  return {
    id: "perf-1",
    upload_status: "completed",
    analysis_result: null,
    analysis_error: null,
    video_url: "athlete-1/clip.mp4",
    performance_type: "practice",
    title: "",
    performance_date: "2026-07-16",
    ...overrides,
  };
}

function renderHero(state: ReturnType<typeof deriveHomeHeroState>) {
  const queryClient = new QueryClient();

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <HeroCard state={state} />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("deriveHomeHeroState", () => {
  it("is the honest first-session state when there is no latest performance - never fabricates one", () => {
    expect(deriveHomeHeroState(undefined)).toEqual({ kind: "first" });
  });

  it("is the processing state for any non-terminal upload_status", () => {
    for (const upload_status of ["uploaded", "analyzing", "processing"]) {
      const state = deriveHomeHeroState(performance({ upload_status }));
      expect(state.kind).toBe("processing");
    }
  });

  it("is the failed state when upload_status is failed", () => {
    const state = deriveHomeHeroState(
      performance({ upload_status: "failed", analysis_error: "Worker unreachable" }),
    );
    expect(state.kind).toBe("failed");
  });

  it("is the reshoot state, carrying the real backend reason, when biomechanics was skipped", () => {
    const state = deriveHomeHeroState(
      performance({ analysis_result: skippedFullBodyNotVisibleFixture }),
    );

    expect(state.kind).toBe("reshoot");
    if (state.kind === "reshoot") {
      expect(state.reason).toBe("Full Body Not Visible");
    }
  });

  it("is the ready state with a real, non-fabricated headline when biomechanics succeeded", () => {
    const state = deriveHomeHeroState(
      performance({ analysis_result: completedWithBiomechanicsFixture }),
    );

    expect(state.kind).toBe("ready");
    if (state.kind === "ready") {
      // 187.5 steps_per_minute in the fixture, rounded by the real
      // cadence metric's own format() - not a value this test invents.
      expect(state.headline).toContain("188");
    }
  });
});

describe("HeroCard rendering", () => {
  it("first-session state: one headline, one action, no fabricated performance data", () => {
    renderHero({ kind: "first" });

    expect(screen.getByText("Ready for your first session?")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /record or upload a clip/i })).toBeInTheDocument();
  });

  it("report-ready state: leads with the real finding and shows real metric chips", () => {
    renderHero({
      kind: "ready",
      performance: performance({ analysis_result: completedWithBiomechanicsFixture }),
      headline: "Your cadence held steady at 188 steps a minute",
    });

    expect(
      screen.getByText("Your cadence held steady at 188 steps a minute"),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /see your full report/i })).toBeInTheDocument();
    // duty_factor is the one EXPERIMENTAL metric in the chip row - must
    // stay honestly labelled, never presented as validated.
    expect(screen.getByText("Experimental")).toBeInTheDocument();
  });

  it("needs-another-recording (reshoot) state: shows the real reason, not an invented one", () => {
    renderHero({
      kind: "reshoot",
      performance: performance({ analysis_result: skippedFullBodyNotVisibleFixture }),
      reason: "Full Body Not Visible",
    });

    expect(screen.getByText("Full Body Not Visible")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /try another recording/i })).toBeInTheDocument();
  });

  it("failed state: uses the four-beat friendly message, never a raw error string", () => {
    renderHero({
      kind: "failed",
      performance: performance({
        upload_status: "failed",
        analysis_error: "ECONNREFUSED 127.0.0.1:8011",
      }),
    });

    expect(screen.queryByText(/ECONNREFUSED/)).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /retry analysis/i })).toBeInTheDocument();
  });
});

describe("AthleteHome full-page empty states (no fabricated data)", () => {
  it("renders every honest empty state at once for a brand-new athlete, and stays mobile-first responsive", async () => {
    const { default: AthleteHome } = await import("./AthleteHome");
    const queryClient = new QueryClient();

    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <AthleteHome />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(screen.getByText("Ready for your first session?")).toBeInTheDocument();
    expect(screen.getByText("Not set yet.")).toBeInTheDocument();
    expect(screen.getByText("No active goal yet.")).toBeInTheDocument();
    expect(
      screen.getByText(/complete your first fully analyzed session/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText("You're all caught up - nothing new to review."),
    ).toBeInTheDocument();
    expect(screen.getByText("No sessions yet.")).toBeInTheDocument();

    // Mobile-first: single column by default, two-column grid only from
    // the lg breakpoint up - never a desktop-only fixed layout.
    const grid = container.querySelector(".grid.grid-cols-1");
    expect(grid).not.toBeNull();
    expect(grid?.className).toContain("lg:grid-cols-[1fr_320px]");
  });
});
