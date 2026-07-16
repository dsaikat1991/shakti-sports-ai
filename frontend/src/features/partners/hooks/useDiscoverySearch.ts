import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  requestConnectionByAthleteId,
  searchDiscoverableAthletes,
} from "../services/discovery.service";

export interface DiscoverySearchFilters {
  event: string | null;
  state: string | null;
}

// Mirrors the RPC's own requirement (migration 0009): at least one
// filter must be set, or the query is disabled entirely rather than
// firing a call that the server would reject anyway.
export function useDiscoverySearch(filters: DiscoverySearchFilters) {
  const hasFilter = Boolean(filters.event || filters.state);

  return useQuery({
    queryKey: ["discovery-search", filters.event, filters.state],
    queryFn: () => searchDiscoverableAthletes({ event: filters.event, state: filters.state }),
    enabled: hasFilter,
  });
}

export function useRequestConnectionByAthleteId() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (targetAthleteId: string) => requestConnectionByAthleteId(targetAthleteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["partner-connections"] });
      queryClient.invalidateQueries({ queryKey: ["athlete-connections"] });
    },
  });
}
