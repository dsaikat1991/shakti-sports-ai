import { useQuery } from "@tanstack/react-query";

import { getConnectionsForCoach, getProfilesByIds } from "../services/connections.service";
import type { BaseProfile, PartnerConnection } from "../types/connection";

export interface EnrichedCoachConnection extends PartnerConnection {
  athleteProfile: BaseProfile | null;
}

// A coach/academy's own connection rows, enriched with each athlete's
// base profile in a second batched query rather than a nested
// PostgREST embed - keeps the join logic explicit and easy to follow,
// and RLS already scopes getProfilesByIds() to exactly the rows this
// caller is allowed to see (see migration 0005), so no extra filtering
// is needed here.
export function usePartnerConnections(coachId?: string) {
  return useQuery({
    queryKey: ["partner-connections", coachId],
    queryFn: async () => {
      if (!coachId) return [];

      const { data: connections, error } = await getConnectionsForCoach(coachId);
      if (error) throw new Error(error.message);

      const rows = (connections ?? []) as PartnerConnection[];
      const athleteIds = rows.map((c) => c.athlete_id);

      const { data: profiles, error: profileError } = await getProfilesByIds(athleteIds);
      if (profileError) throw new Error(profileError.message);

      const profileMap = new Map(
        ((profiles ?? []) as BaseProfile[]).map((p) => [p.id, p]),
      );

      return rows.map((c) => ({
        ...c,
        athleteProfile: profileMap.get(c.athlete_id) ?? null,
      })) satisfies EnrichedCoachConnection[];
    },
    enabled: Boolean(coachId),
  });
}
