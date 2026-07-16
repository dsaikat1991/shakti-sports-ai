import { useAthleteConnections } from "../../partners/hooks/useAthleteConnections";
import { usePerformances } from "../../performances/hooks/usePerformances";
import { useAuth } from "../../auth/context/AuthContext";
import { deriveNotifications } from "../lib/deriveNotifications";

// Composes data that's already fetched elsewhere (performances,
// coach connections) rather than adding a new query or table - see
// docs/ENGINEERING_HANDOFF.md for the "derived, not stored" reasoning.
export function useAthleteNotifications() {
  const { user } = useAuth();
  const performances = usePerformances(user?.id);
  const connections = useAthleteConnections(user?.id);

  const notifications = deriveNotifications(
    (performances.data ?? []) as any,
    connections.data ?? [],
    user?.id,
  );

  return {
    notifications,
    isLoading: performances.isLoading || connections.isLoading,
    error: performances.error ?? connections.error,
  };
}
