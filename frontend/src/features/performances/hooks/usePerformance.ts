import { useQuery } from "@tanstack/react-query";
import { getPerformanceById } from "../services/performance.service";

export function usePerformance(performanceId?: string) {
  return useQuery({
    queryKey: ["performance", performanceId],
    queryFn: async () => {
      if (!performanceId) {
        throw new Error("Performance ID is required.");
      }

      const { data, error } = await getPerformanceById(performanceId);

      if (error) {
        throw new Error(error.message);
      }

      return data;
    },
    enabled: Boolean(performanceId),
  });
}