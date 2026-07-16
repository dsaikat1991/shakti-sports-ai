import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  type ListType,
  addListMember,
  createList,
  deleteList,
  getListMembers,
  getLists,
  removeListMember,
} from "../services/discovery.service";

export function useAthleteLists(ownerId?: string) {
  return useQuery({
    queryKey: ["athlete-lists", ownerId],
    queryFn: async () => {
      if (!ownerId) return [];
      const { data, error } = await getLists(ownerId);
      if (error) throw new Error(error.message);
      return data ?? [];
    },
    enabled: Boolean(ownerId),
  });
}

export function useCreateList(ownerId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: { name: string; listType: ListType }) => {
      if (!ownerId) throw new Error("Not signed in.");
      const { data, error } = await createList(ownerId, input.name, input.listType);
      if (error) throw new Error(error.message);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-lists", ownerId] });
    },
  });
}

export function useDeleteList(ownerId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (listId: string) => {
      const { error } = await deleteList(listId);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-lists", ownerId] });
    },
  });
}

export function useListMembers(listId?: string) {
  return useQuery({
    queryKey: ["athlete-list-members", listId],
    queryFn: async () => {
      if (!listId) return [];
      const { data, error } = await getListMembers(listId);
      if (error) throw new Error(error.message);
      return data ?? [];
    },
    enabled: Boolean(listId),
  });
}

export function useAddListMember(listId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (athleteId: string) => {
      if (!listId) throw new Error("No list selected.");
      const { error } = await addListMember(listId, athleteId);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-list-members", listId] });
    },
  });
}

export function useRemoveListMember(listId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (memberId: string) => {
      const { error } = await removeListMember(memberId);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athlete-list-members", listId] });
    },
  });
}
