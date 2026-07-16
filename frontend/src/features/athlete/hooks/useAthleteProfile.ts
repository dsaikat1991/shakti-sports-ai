import { useQuery } from "@tanstack/react-query";

import { getBaseProfile, getSportingProfile } from "../services/athleteProfile.service";

export function useAthleteProfile(athleteId?: string) {
  return useQuery({
    queryKey: ["athlete-profile", athleteId],
    queryFn: async () => {
      if (!athleteId) return null;

      const [baseResult, sportingResult] = await Promise.all([
        getBaseProfile(athleteId),
        getSportingProfile(athleteId),
      ]);

      if (baseResult.error) throw new Error(baseResult.error.message);
      if (sportingResult.error) throw new Error(sportingResult.error.message);

      return {
        base: baseResult.data,
        sporting: sportingResult.data,
      };
    },
    enabled: Boolean(athleteId),
  });
}
