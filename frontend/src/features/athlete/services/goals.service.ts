import { supabase } from "../../../lib/supabase";

export type GoalStatus = "active" | "completed" | "abandoned";

export interface AthleteGoal {
  id: string;
  athlete_id: string;
  description: string;
  target_date: string | null;
  status: GoalStatus;
  created_at: string;
  updated_at: string;
}

const GOAL_COLUMNS = "id, athlete_id, description, target_date, status, created_at, updated_at";

export async function getGoals(athleteId: string) {
  return supabase
    .from("athlete_goals")
    .select(GOAL_COLUMNS)
    .eq("athlete_id", athleteId)
    .order("created_at", { ascending: false });
}

export async function createGoal(
  athleteId: string,
  input: { description: string; target_date: string | null },
) {
  return supabase
    .from("athlete_goals")
    .insert({
      athlete_id: athleteId,
      description: input.description,
      target_date: input.target_date,
      status: "active",
    })
    .select(GOAL_COLUMNS)
    .single();
}

export async function updateGoalStatus(goalId: string, status: GoalStatus) {
  return supabase
    .from("athlete_goals")
    .update({ status, updated_at: new Date().toISOString() })
    .eq("id", goalId)
    .select(GOAL_COLUMNS)
    .single();
}

export async function deleteGoal(goalId: string) {
  return supabase.from("athlete_goals").delete().eq("id", goalId);
}
