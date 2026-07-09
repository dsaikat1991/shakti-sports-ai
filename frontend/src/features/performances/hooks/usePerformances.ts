import { useQuery } from "@tanstack/react-query";
import { getAthletePerformances } from "../services/performance.service";

export function usePerformances(athleteId?: string) {
  return useQuery({
    queryKey: ["performances", athleteId],
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