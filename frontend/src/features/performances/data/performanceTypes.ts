import type { PerformanceType } from "../types/performance";

export const PERFORMANCE_TYPES: {
  id: PerformanceType;
  title: string;
  description: string;
}[] = [
  {
    id: "practice",
    title: "Practice",
    description: "A regular training session to track improvement.",
  },
  {
    id: "competition",
    title: "Competition",
    description: "A race, jump, meet, or official performance.",
  },
  {
    id: "trial",
    title: "Trial",
    description: "A selection trial, academy test, or coach evaluation.",
  },
  {
    id: "assessment",
    title: "Assessment",
    description: "A technical check focused on form and movement quality.",
  },
];