import { useQuery } from "@tanstack/react-query";
import { getAthletePerformances } from "../../performances/services/performance.service";

export function useAthleteDashboard(athleteId?: string) {
  return useQuery({
    queryKey: ["athlete-dashboard", athleteId],
    queryFn: async () => {
      if (!athleteId) return [];

      const { data, error } = await getAthletePerformances(athleteId);

      if (error) {
        throw new Error(error.message);
      }

      return data ?? [];
    },
    enabled: Boolean(athleteId),
  });
}