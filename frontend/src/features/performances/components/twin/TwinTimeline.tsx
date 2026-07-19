import TwinSessionCard, { type TwinSessionCardProps } from "./TwinSessionCard";
import EmptyState from "../../../../components/shared/EmptyState";
import { CalendarClock } from "lucide-react";

export default function TwinTimeline({ sessions }: { sessions: TwinSessionCardProps[] }) {
  if (sessions.length === 0) {
    return (
      <EmptyState
        icon={CalendarClock}
        title="Your progress starts with your first upload"
        description="Upload a performance to begin building your evolving athlete profile."
      />
    );
  }

  return (
    <div className="space-y-4">
      {sessions.map((session) => (
        <TwinSessionCard key={session.reportHref} {...session} />
      ))}
    </div>
  );
}
