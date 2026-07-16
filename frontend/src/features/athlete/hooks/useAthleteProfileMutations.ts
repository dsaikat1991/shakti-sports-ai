import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  type BaseProfileUpdate,
  type SportingProfileUpdate,
  setAccountDeletionRequested,
  updateAiTrainingConsent,
  updateBaseProfile,
  updateSportingProfile,
} from "../services/athleteProfile.service";

export function useUpdateAthleteProfile(athleteId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: {
      base: BaseProfileUpdate;
      sporting: SportingProfileUpdate;
    }) => {
      if (!athleteId) throw new Error("Not signed in.");

      const [baseResult, sportingResult] = await Promise.all([
        updateBaseProfile(athleteId, input.base),
        updateSportingProfile(athleteId, input.sporting),
      ]);

      if (baseResult.error) throw new Error(baseResult.error.message);
      if (sportingResult.error) throw new Error(sportingResult.error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-profile", athleteId] });
    },
  });
}

export function useUpdateAiTrainingConsent(athleteId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (consent: boolean) => {
      if (!athleteId) throw new Error("Not signed in.");
      const { error } = await updateAiTrainingConsent(athleteId, consent);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-profile", athleteId] });
    },
  });
}

export function useSetAccountDeletionRequested(athleteId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (requested: boolean) => {
      if (!athleteId) throw new Error("Not signed in.");
      const { error } = await setAccountDeletionRequested(athleteId, requested);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-profile", athleteId] });
    },
  });
}
