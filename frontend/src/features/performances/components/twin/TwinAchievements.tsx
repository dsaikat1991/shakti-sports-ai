import { Award, CheckCircle2 } from "lucide-react";
import { formatSessionDate } from "../../lib/analysisSummary";

export interface CompletedGoal {
  description: string;
  updatedAt: string;
}

// Surfaces existing, already-editable athlete data (athlete_profiles.
// achievements, completed athlete_goals rows) rather than inventing a
// new achievements concept - both already exist and were simply never
// shown together as part of the athlete's identity narrative before.
export default function TwinAchievements({
  achievementsText,
  completedGoals,
}: {
  achievementsText: string | null;
  completedGoals: CompletedGoal[];
}) {
  const hasContent = Boolean(achievementsText) || completedGoals.length > 0;

  if (!hasContent) {
    return (
      <div className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-6 text-center">
        <Award className="mx-auto h-9 w-9 text-gray-400" />
        <p className="mt-3 text-sm text-gray-500">
          No achievements recorded yet - add them to your profile, or complete a goal.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {achievementsText && (
        <div className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <Award className="h-4 w-4 text-[#F0600E]" />
            <p className="text-xs font-bold uppercase tracking-widest text-gray-400">Achievements</p>
          </div>
          <p className="mt-2 whitespace-pre-line text-sm leading-6 text-gray-700">{achievementsText}</p>
        </div>
      )}

      {completedGoals.length > 0 && (
        <div className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-green-700" />
            <p className="text-xs font-bold uppercase tracking-widest text-gray-400">Completed Goals</p>
          </div>
          <ul className="mt-3 space-y-2">
            {completedGoals.map((goal) => (
              <li key={goal.description + goal.updatedAt} className="flex items-start justify-between gap-3 text-sm">
                <span className="text-gray-700">{goal.description}</span>
                <span className="shrink-0 text-xs text-gray-400">{formatSessionDate(goal.updatedAt)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
