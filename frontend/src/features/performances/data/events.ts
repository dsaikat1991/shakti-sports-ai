import type { PerformanceEvent } from "../types/performance";

export const EVENTS: {
  id: PerformanceEvent;
  title: string;
  subtitle: string;
  description: string;
}[] = [
  {
    id: "100m",
    title: "100m Sprint",
    subtitle: "Acceleration · Top Speed",
    description:
      "Best for straight-line speed, stride length, cadence and ground contact analysis.",
  },
  {
    id: "110h",
    title: "Hurdles",
    subtitle: "Rhythm · Clearance",
    description:
      "Analyze lead leg, trail leg, hurdle clearance, landing balance and split timing.",
  },
  {
    id: "long_jump",
    title: "Long Jump",
    subtitle: "Run-up · Take-off · Landing",
    description:
      "Measure approach speed, take-off angle, board contact and landing efficiency.",
  },
  {
    id: "high_jump",
    title: "High Jump",
    subtitle: "Curve · Lift · Clearance",
    description:
      "Review approach curve, take-off foot, vertical lift, hip clearance and landing safety.",
  },
];