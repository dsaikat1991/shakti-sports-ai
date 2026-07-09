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
  performedOn: string;
  title: string;
  notes: string;
  recording: File | null;
}