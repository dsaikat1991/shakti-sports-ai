import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getAvatarSignedUrl, removeAvatar, uploadAvatar } from "../services/avatar.service";

// Shared by any component that needs to render an avatar from its
// storage path (Profile page, UserMenu) - one signed-URL fetch per path,
// cached by React Query rather than re-signed on every render.
export function useAvatarSignedUrl(path?: string | null) {
  return useQuery({
    queryKey: ["avatar-signed-url", path],
    queryFn: () => getAvatarSignedUrl(path as string),
    enabled: Boolean(path),
    staleTime: 30 * 60 * 1000,
  });
}

// UserMenu (shared across every layout) keeps its own avatar-path query,
// separate from useAthleteProfile - it can't depend on an athlete-only
// hook (coach/academy accounts have no athlete_profiles row). Both
// caches need invalidating together, or the header goes stale on the
// next mutation until a full reload.
function invalidateAvatarQueries(
  queryClient: ReturnType<typeof useQueryClient>,
  userId?: string,
) {
  queryClient.invalidateQueries({ queryKey: ["athlete-profile", userId] });
  queryClient.invalidateQueries({ queryKey: ["own-avatar-path", userId] });
}

export function useUploadAvatar(userId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      if (!userId) throw new Error("Not signed in.");
      return uploadAvatar(userId, file);
    },
    onSuccess: (path) => {
      invalidateAvatarQueries(queryClient, userId);
      // Same path as before an upsert re-upload - the cached signed URL
      // for it would otherwise keep serving (via browser image caching)
      // whatever was fetched under the old content, not the new photo.
      queryClient.invalidateQueries({ queryKey: ["avatar-signed-url", path] });
    },
  });
}

export function useRemoveAvatar(userId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (path: string) => {
      if (!userId) throw new Error("Not signed in.");
      return removeAvatar(userId, path);
    },
    onSuccess: (_data, path) => {
      invalidateAvatarQueries(queryClient, userId);
      queryClient.invalidateQueries({ queryKey: ["avatar-signed-url", path] });
    },
  });
}
