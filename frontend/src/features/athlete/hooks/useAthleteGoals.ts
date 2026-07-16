import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  type GoalStatus,
  createGoal,
  deleteGoal,
  getGoals,
  updateGoalStatus,
} from "../services/goals.service";

export function useAthleteGoals(athleteId?: string) {
  return useQuery({
    queryKey: ["athlete-goals", athleteId],
    queryFn: async () => {
      if (!athleteId) return [];
      const { data, error } = await getGoals(athleteId);
      if (error) throw new Error(error.message);
      return data ?? [];
    },
    enabled: Boolean(athleteId),
  });
}

export function useCreateGoal(athleteId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: { description: string; target_date: string | null }) => {
      if (!athleteId) throw new Error("Not signed in.");
      const { data, error } = await createGoal(athleteId, input);
      if (error) throw new Error(error.message);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-goals", athleteId] });
    },
  });
}

export function useUpdateGoalStatus(athleteId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ goalId, status }: { goalId: string; status: GoalStatus }) => {
      const { error } = await updateGoalStatus(goalId, status);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-goals", athleteId] });
    },
  });
}

export function useDeleteGoal(athleteId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (goalId: string) => {
      const { error } = await deleteGoal(goalId);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-goals", athleteId] });
    },
  });
}
