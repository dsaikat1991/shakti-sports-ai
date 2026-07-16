import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createBookmark,
  getBookmarkedAthleteCards,
  removeBookmark,
} from "../services/discovery.service";

export function useBookmarkedAthletes(enabled: boolean) {
  return useQuery({
    queryKey: ["coach-bookmarks"],
    queryFn: getBookmarkedAthleteCards,
    enabled,
  });
}

export function useCreateBookmark(coachId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (athleteId: string) => {
      if (!coachId) throw new Error("Not signed in.");
      const { error } = await createBookmark(coachId, athleteId);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coach-bookmarks"] });
    },
  });
}

export function useRemoveBookmark() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (bookmarkId: string) => {
      const { error } = await removeBookmark(bookmarkId);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coach-bookmarks"] });
    },
  });
}
