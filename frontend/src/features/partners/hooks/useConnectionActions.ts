import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  requestPartnerConnection,
  respondToConnection,
  revokeConnection,
} from "../services/connections.service";

// Both sides' connection lists key off the same underlying table, so
// any mutation here can affect what either the coach/academy view or
// the athlete view should show next - invalidate both broadly rather
// than trying to track exactly which side changed.
function invalidateConnectionQueries(
  queryClient: ReturnType<typeof useQueryClient>,
) {
  queryClient.invalidateQueries({ queryKey: ["partner-connections"] });
  queryClient.invalidateQueries({ queryKey: ["athlete-connections"] });
}

export function useRequestConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (targetEmail: string) => requestPartnerConnection(targetEmail),
    onSuccess: () => invalidateConnectionQueries(queryClient),
  });
}

export function useRespondToConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      connectionId,
      status,
    }: {
      connectionId: string;
      status: "accepted" | "rejected";
    }) => {
      const { data, error } = await respondToConnection(connectionId, status);
      if (error) throw new Error(error.message);
      return data;
    },
    onSuccess: () => invalidateConnectionQueries(queryClient),
  });
}

export function useRevokeConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (connectionId: string) => {
      const { data, error } = await revokeConnection(connectionId);
      if (error) throw new Error(error.message);
      return data;
    },
    onSuccess: () => invalidateConnectionQueries(queryClient),
  });
}
