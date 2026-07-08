export type PerformanceEvent =
  | "100m"
  | "110h"
  | "long_jump"
  | "high_jump";

export type PerformanceType =
  | "practice"
  | "competition"
  | "trial"
  | "assessment";

export interface PerformanceDraft {
  event?: PerformanceEvent;

  performanceType?: PerformanceType;

  title: string;

  notes: string;

  recordedAt?: string;

  recording?: File | null;
}