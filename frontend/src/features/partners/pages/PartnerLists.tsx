import { ArrowRight, ListChecks, Loader2, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { useCreateList, useAthleteLists, useDeleteList } from "../hooks/useAthleteLists";
import type { ListType } from "../services/discovery.service";

const LIST_TYPE_OPTIONS: { value: ListType; label: string }[] = [
  { value: "TOURNAMENT_SELECTION", label: "Tournament Selection" },
  { value: "CAMP_SELECTION", label: "Camp Selection" },
  { value: "TRIAL_SELECTION", label: "Trial Selection" },
  { value: "TEAM_SQUAD", label: "Team Squad" },
];

function listTypeLabel(type: string) {
  return LIST_TYPE_OPTIONS.find((opt) => opt.value === type)?.label ?? type;
}

export default function PartnerLists() {
  const { user, role } = useAuth();
  const isAcademy = role === "academy";
  const routeSet = isAcademy ? ROUTES.ACADEMY : ROUTES.COACH;

  const { data: lists = [], isLoading, error } = useAthleteLists(user?.id);
  const createList = useCreateList(user?.id);
  const deleteList = useDeleteList(user?.id);

  const [name, setName] = useState("");
  const [listType, setListType] = useState<ListType>("TRIAL_SELECTION");

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    createList.mutate(
      { name: name.trim(), listType },
      { onSuccess: () => setName("") },
    );
  }

  return (
    <div className="mx-auto max-w-6xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        Roster Selections
      </p>
      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        Lists
      </h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        Named selections of your connected athletes for a tournament, camp,
        trial, or squad. Only currently-connected athletes can be added.
      </p>

      <form
        onSubmit={handleCreate}
        className="mt-8 flex flex-col gap-3 rounded-3xl border border-gray-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center"
      >
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. State Trials 2026"
          className="flex-1 rounded-xl border border-gray-200 px-4 py-2.5 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
        />

        <select
          value={listType}
          onChange={(e) => setListType(e.target.value as ListType)}
          className="rounded-xl border border-gray-200 px-3 py-2.5 text-sm outline-none focus:border-[#F0600E]"
        >
          {LIST_TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        <button
          type="submit"
          disabled={!name.trim() || createList.isPending}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#F0600E] px-5 py-2.5 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Plus className="h-4 w-4" />
          Create List
        </button>
      </form>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading your lists...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-700">
          {error.message}
        </div>
      )}

      {!isLoading && !error && lists.length === 0 && (
        <div className="mt-10 rounded-4xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center">
          <ListChecks className="mx-auto h-11 w-11 text-gray-400" />
          <h2 className="mt-5 text-2xl font-bold text-gray-950">No lists yet</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
            Create your first list above to start organizing selections.
          </p>
        </div>
      )}

      {!isLoading && lists.length > 0 && (
        <div className="mt-8 space-y-4">
          {lists.map((list) => (
            <div
              key={list.id}
              className="flex items-center justify-between rounded-4xl border border-gray-200 bg-white p-6 shadow-sm"
            >
              <div>
                <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.18em] text-[#F0600E]">
                  {listTypeLabel(list.list_type)}
                </p>
                <h2 className="mt-2 text-xl font-bold text-gray-950">{list.name}</h2>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => deleteList.mutate(list.id)}
                  disabled={deleteList.isPending}
                  className="flex h-10 w-10 items-center justify-center rounded-xl border border-gray-200 text-gray-500 transition hover:border-red-300 hover:text-red-600 disabled:opacity-50"
                  aria-label="Delete list"
                >
                  <Trash2 className="h-4 w-4" />
                </button>

                <Link
                  to={routeSet.LIST_DETAIL(list.id)}
                  className="inline-flex items-center gap-2 text-sm font-bold text-gray-700 hover:text-[#F0600E]"
                >
                  View
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
