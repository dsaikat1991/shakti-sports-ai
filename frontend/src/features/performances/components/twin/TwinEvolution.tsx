import { History } from "lucide-react";
import EmptyState from "../../../../components/shared/EmptyState";

// Step 9 - every line is template-filled from generateEvolutionStatements()
// (twinEngine.ts) using analyzeTrend()'s own numbers - never free-
// generated or LLM-produced text.
export default function TwinEvolution({ statements }: { statements: string[] }) {
  if (statements.length === 0) {
    return (
      <EmptyState
        icon={History}
        tone="neutral"
        title="Not enough data yet"
        description="Evolution statements appear once a metric shows a real, sustained change across your analysed sessions."
      />
    );
  }

  return (
    <ul className="space-y-3">
      {statements.map((statement) => (
        <li
          key={statement}
          className="flex items-start gap-3 rounded-2xl border border-gray-200 bg-white p-4 text-sm leading-6 text-gray-700 shadow-sm"
        >
          <History className="mt-0.5 h-4 w-4 shrink-0 text-[#F0600E]" />
          {statement}
        </li>
      ))}
    </ul>
  );
}
