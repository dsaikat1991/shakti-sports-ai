import { CheckCircle2, Loader2, Target, Trash2, XCircle } from "lucide-react";
import { useState } from "react";

import EmptyState from "../../../components/shared/EmptyState";
import { useAuth } from "../../auth/context/AuthContext";
import {
  useAthleteGoals,
  useCreateGoal,
  useDeleteGoal,
  useUpdateGoalStatus,
} from "../hooks/useAthleteGoals";
import type { AthleteGoal, GoalStatus } from "../services/goals.service";

function formatDate(date?: string | null) {
  if (!date) return null;
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

function statusClasses(status: GoalStatus) {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-700";
    case "abandoned":
      return "bg-gray-200 text-gray-600";
    default:
      return "bg-orange-100 text-[#F0600E]";
  }
}

function GoalCard({
  goal,
  onUpdateStatus,
  onDelete,
  isMutating,
}: {
  goal: AthleteGoal;
  onUpdateStatus: (status: GoalStatus) => void;
  onDelete: () => void;
  isMutating: boolean;
}) {
  const targetDate = formatDate(goal.target_date);

  return (
    <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusClasses(goal.status)}`}>
            {goal.status.charAt(0).toUpperCase() + goal.status.slice(1)}
          </span>
          <p className="mt-3 text-lg font-bold text-gray-950">{goal.description}</p>
          {targetDate && (
            <p className="mt-1 text-sm text-gray-500">Target: {targetDate}</p>
          )}
        </div>

        <button
          type="button"
          onClick={onDelete}
          disabled={isMutating}
          className="shrink-0 text-gray-400 transition hover:text-red-600 disabled:opacity-50"
          aria-label="Delete goal"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {goal.status === "active" && (
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            disabled={isMutating}
            onClick={() => onUpdateStatus("completed")}
            className="inline-flex items-center gap-1 rounded-xl bg-[#F0600E] px-4 py-2 text-sm font-bold text-white transition hover:bg-orange-700 disabled:opacity-50"
          >
            <CheckCircle2 className="h-4 w-4" />
            Mark Complete
          </button>
          <button
            type="button"
            disabled={isMutating}
            onClick={() => onUpdateStatus("abandoned")}
            className="inline-flex items-center gap-1 rounded-xl border border-gray-300 px-4 py-2 text-sm font-bold text-gray-700 transition hover:border-gray-400 disabled:opacity-50"
          >
            <XCircle className="h-4 w-4" />
            Abandon
          </button>
        </div>
      )}
    </div>
  );
}

export default function AthleteGoals() {
  const { user } = useAuth();
  const { data: goals = [], isLoading, error } = useAthleteGoals(user?.id);
  const createGoal = useCreateGoal(user?.id);
  const updateStatus = useUpdateGoalStatus(user?.id);
  const deleteGoal = useDeleteGoal(user?.id);

  const [description, setDescription] = useState("");
  const [targetDate, setTargetDate] = useState("");

  const activeGoals = goals.filter((g) => g.status === "active");
  const pastGoals = goals.filter((g) => g.status !== "active");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!description.trim()) return;

    createGoal.mutate(
      { description: description.trim(), target_date: targetDate || null },
      {
        onSuccess: () => {
          setDescription("");
          setTargetDate("");
        },
      },
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        Goals
      </p>
      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        Your Goals
      </h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        Set what you're working toward. AI-generated training recommendations
        based on your goals are planned for later - this is just the record
        for now.
      </p>

      <form onSubmit={handleSubmit} className="mt-10 rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold text-gray-950">Add a goal</h2>

        <div className="mt-4 grid gap-3 sm:grid-cols-[1fr_auto_auto]">
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g. Break 11.5s in the 100m"
            required
            className="rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
          />
          <input
            type="date"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            className="rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
          />
          <button
            type="submit"
            disabled={createGoal.isPending}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {createGoal.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Add Goal
          </button>
        </div>

        {createGoal.isError && (
          <p className="mt-3 text-sm font-semibold text-red-600">
            {(createGoal.error as Error).message}
          </p>
        )}
      </form>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading your goals...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-700">
          {error.message}
        </div>
      )}

      {!isLoading && activeGoals.length === 0 && pastGoals.length === 0 && (
        <EmptyState
          icon={Target}
          title="No goals yet"
          description="Add your first goal above to start tracking what you're working toward."
        />
      )}

      {activeGoals.length > 0 && (
        <div className="mt-10">
          <h2 className="text-lg font-bold text-gray-950">Active</h2>
          <div className="mt-4 space-y-3">
            {activeGoals.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                isMutating={updateStatus.isPending || deleteGoal.isPending}
                onUpdateStatus={(status) => updateStatus.mutate({ goalId: goal.id, status })}
                onDelete={() => deleteGoal.mutate(goal.id)}
              />
            ))}
          </div>
        </div>
      )}

      {pastGoals.length > 0 && (
        <div className="mt-10">
          <h2 className="text-lg font-bold text-gray-950">Past</h2>
          <div className="mt-4 space-y-3">
            {pastGoals.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                isMutating={updateStatus.isPending || deleteGoal.isPending}
                onUpdateStatus={(status) => updateStatus.mutate({ goalId: goal.id, status })}
                onDelete={() => deleteGoal.mutate(goal.id)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
