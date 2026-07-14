import type { AnalysisResult } from "../types/analysis";

// Confirmed real shapes, captured from live backend responses this session
// (see docs/ENGINEERING_HANDOFF.md section 6 for the general contract).
// Using these instead of writing test data into Supabase for every UI
// change - see PerformanceDetail.test.tsx.

// Real completed job for examples/my_sprint_3.mp4 (job id
// 8e07b0ac-11ab-453e-8654-b25789850e8b) - biomechanics skipped by the
// quality gate because ankles/feet aren't consistently visible in that
// clip's narrow portrait framing.
export const skippedBiomechanicsFixture: AnalysisResult = {
  provider: "rtmpose",
  video: { total_frames: 290, fps: 24, duration_seconds: 12.08 },
  analysis: { frames_with_pose: 290, detection_rate_percent: 100 },
  recording_quality: {
    rating: "Excellent",
    overall_score: 92.88,
    biomechanics_ready: false,
    camera_view: {
      classification: "Side View",
      confidence: 91.25,
      suitable_for_sprint: true,
      required_view: "Side View",
    },
    warnings: [
      "Ankles are not consistently visible.",
      "Feet are not consistently visible.",
    ],
    recommendations: [],
  },
  tracking_summary: {
    status_counts: { tracked: 289, selected: 1 },
    observed_ratio: 1,
    observed_frames: 290,
  },
  biomechanics: { status: "skipped", reason: "Not Ready for Analysis" },
};

// Hybrid: recording_quality/video/tracking_summary are the real completed
// live-API result for examples/my_sprint_2.mp4 (job
// ef9bbf96-67bd-42f9-b456-38e38f46feb1, which itself had biomechanics
// skipped by the quality gate). biomechanics.segments are real output from
// `scripts/sprint_report.py` on the same clip, which bypasses the live
// quality gate - combined here because no available example clip clears
// the gate end-to-end. No values are invented.
//
// The joint_angles key order below is deliberately the order Postgres's
// jsonb column type actually returns (sorted by key length, then
// alphabetically) rather than the "natural" order - this is what a real
// round-trip through analysis_result looks like, and is what caught the
// joint-angle ordering bug this fixture guards against.
export const completedWithBiomechanicsFixture: AnalysisResult = {
  provider: "rtmpose",
  video: { total_frames: 787, fps: 50, duration_seconds: 15.74 },
  analysis: { frames_with_pose: 787, detection_rate_percent: 100 },
  recording_quality: {
    rating: "Excellent",
    overall_score: 92.17,
    biomechanics_ready: false,
    camera_view: {
      classification: "Side View",
      confidence: 97.35,
      suitable_for_sprint: true,
      required_view: "Side View",
    },
    warnings: [
      "The athlete appears too far from the camera.",
      "The camera appears to be positioned low and angled upward, leaving excess empty space above the athlete.",
    ],
    recommendations: [
      "Move the camera closer while keeping the full body visible.",
      "Raise the camera to about the athlete's waist-to-shoulder height and keep the shot level, rather than shooting up from near the ground.",
    ],
  },
  tracking_summary: {
    status_counts: { selected: 1, tracked: 786 },
    observed_frames: 787,
    observed_ratio: 1,
  },
  biomechanics: {
    provider: "rtmpose",
    fps: 50,
    observed_frames: 787,
    interpolated_frames: 0,
    unbridged_gaps: 0,
    segments: [
      {
        status: "completed",
        segment: {
          start_frame_index: 0,
          end_frame_index: 786,
          frame_count: 787,
          duration_ms: 15720,
        },
        frames_analyzed: 787,
        cadence: {
          status: "experimental",
          steps_per_minute: 187.5,
          events_used: 46,
          method: "alternating_peak_knee_flexion_proxy",
        },
        stride: {
          status: "experimental",
          stride_frequency_hz: 1.562,
          median_stride_duration_ms: 640,
          cycles_used: 44,
        },
        ground_contact: {
          status: "experimental",
          events: 46,
          median_contact_time_ms: 80,
        },
        flight_time: {
          status: "experimental",
          median_flight_time_ms: 260,
          events_used: 43,
        },
        duty_factor_percent: 23.53,
        knee_symmetry_score: 85.98,
        // Deliberately jsonb-scrambled order: left_hip, left_knee,
        // right_hip, left_elbow, right_knee, right_elbow.
        joint_angles: {
          left_hip: {
            label: "Left hip angle",
            coverage_percent: 97.97,
            mean_degrees: 174.6,
            min_degrees: 158.54,
            max_degrees: 179.56,
            range_degrees: 14.7,
          },
          left_knee: {
            label: "Left knee angle",
            coverage_percent: 97.2,
            mean_degrees: 146.71,
            min_degrees: 52.24,
            max_degrees: 176.65,
            range_degrees: 95.32,
          },
          right_hip: {
            label: "Right hip angle",
            coverage_percent: 97.33,
            mean_degrees: 172.88,
            min_degrees: 153.51,
            max_degrees: 178.95,
            range_degrees: 16.61,
          },
          left_elbow: {
            label: "Left elbow angle",
            coverage_percent: 96.95,
            mean_degrees: 79.35,
            min_degrees: 9.12,
            max_degrees: 178.38,
            range_degrees: 147.68,
          },
          right_knee: {
            label: "Right knee angle",
            coverage_percent: 96.19,
            mean_degrees: 156.09,
            min_degrees: 59.34,
            max_degrees: 179.3,
            range_degrees: 81.96,
          },
          right_elbow: {
            label: "Right elbow angle",
            coverage_percent: 93.52,
            mean_degrees: 95.32,
            min_degrees: 1.24,
            max_degrees: 177.58,
            range_degrees: 166.93,
          },
        },
        limitations: [
          "Angles remain projected 2D image-plane measurements.",
          "Ground contact, flight time, and duty factor have a CONFIRMED issue for low/close camera angles.",
          "These outputs are not laboratory or force-plate validated.",
        ],
      },
    ],
  } as unknown as AnalysisResult["biomechanics"],
};

// Synthetic edge case (test-only, not captured from a real response): a
// segment with some fields missing/null, to exercise the "N/A" / "-"
// fallback rendering paths that no available real clip happens to hit.
export const completedWithMissingValuesFixture: AnalysisResult = {
  ...completedWithBiomechanicsFixture,
  biomechanics: {
    ...(completedWithBiomechanicsFixture.biomechanics as any),
    segments: [
      {
        ...(completedWithBiomechanicsFixture.biomechanics as any).segments[0],
        cadence: { status: "insufficient_data" },
        duty_factor_percent: null,
        knee_symmetry_score: null,
        flight_time: { status: "insufficient_data" },
        joint_angles: {
          left_knee: {
            label: "Left knee angle",
            coverage_percent: null,
            mean_degrees: null,
            min_degrees: null,
            max_degrees: null,
            range_degrees: null,
          },
        },
        limitations: [],
      },
    ],
  } as unknown as AnalysisResult["biomechanics"],
};
