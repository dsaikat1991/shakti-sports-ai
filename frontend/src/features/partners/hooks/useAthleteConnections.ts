import { useQuery } from "@tanstack/react-query";

import { getConnectionsForAthlete, getProfilesByIds } from "../services/connections.service";
import type { BaseProfile, PartnerConnection } from "../types/connection";

export interface EnrichedAthleteConnection extends PartnerConnection {
  partnerProfile: BaseProfile | null;
}

// An athlete's own connection rows, enriched with each coach/academy's
// base profile. Same batched-query-plus-merge shape as
// usePartnerConnections, mirrored for the other side of the
// relationship.
export function useAthleteConnections(athleteId?: string) {
  return useQuery({
    queryKey: ["athlete-connections", athleteId],
    queryFn: async () => {
      if (!athleteId) return [];

      const { data: connections, error } = await getConnectionsForAthlete(athleteId);
      if (error) throw new Error(error.message);

      const rows = (connections ?? []) as PartnerConnection[];
      const coachIds = rows.map((c) => c.coach_id);

      const { data: profiles, error: profileError } = await getProfilesByIds(coachIds);
      if (profileError) throw new Error(profileError.message);

      const profileMap = new Map(
        ((profiles ?? []) as BaseProfile[]).map((p) => [p.id, p]),
      );

      return rows.map((c) => ({
        ...c,
        partnerProfile: profileMap.get(c.coach_id) ?? null,
      })) satisfies EnrichedAthleteConnection[];
    },
    enabled: Boolean(athleteId),
  });
}
