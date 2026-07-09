import { CalendarDays, FileVideo, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { usePerformances } from "../hooks/usePerformances";

function statusLabel(status: string | null) {
  if (status === "completed") return "Completed";
  if (status === "analyzing") return "Analyzing";
  if (status === "failed") return "Failed";
  return "Uploaded";
}
function getEventName(events: unknown) {
  if (Array.isArray(events)) {
    const firstEvent = events[0] as { name?: string } | undefined;
    return firstEvent?.name ?? "Performance";
  }

  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }

  return "Performance";
}
export default function PerformanceHistory() {
  const { user } = useAuth();
  const { data, isLoading, error } = usePerformances(user?.id);

  return (
    <div className="mx-auto max-w-6xl">
      <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
        <div>
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
            Performance History
          </p>

          <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
            Your Performance Timeline
          </h1>

          <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
            Review every uploaded session and track your progress over time.
          </p>
        </div>

        <Link
          to={ROUTES.ATHLETE.NEW_PERFORMANCE}
          className="rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
        >
          Start New Performance
        </Link>
      </div>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-gray-600">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading performances...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl bg-red-50 p-6 text-sm font-semibold text-red-700">
          {error.message}
        </div>
      )}

      {!isLoading && data?.length === 0 && (
        <div className="mt-10 rounded-4xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center">
          <FileVideo className="mx-auto h-10 w-10 text-gray-400" />

          <h3 className="mt-4 text-xl font-bold text-gray-950">
            No performances yet.
          </h3>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
            Start your first performance to build your timeline and prepare your
            first AI report.
          </p>
        </div>
      )}

      <div className="mt-10 space-y-4">
        {data?.map((performance) => (
          <div
            key={performance.id}
            className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl hover:shadow-gray-200"
          >
            <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <h3 className="text-xl font-bold text-gray-950">
                    {performance.title}
                  </h3>

                  <span className="rounded-full bg-orange-50 px-3 py-1 text-xs font-bold text-[#F0600E]">
                    {statusLabel(performance.upload_status)}
                  </span>
                </div>

                <p className="mt-2 flex items-center gap-2 text-sm text-gray-500">
                  <CalendarDays className="h-4 w-4" />
                  {performance.performance_date} ·{" "}
                  {getEventName(performance.events)}
                </p>
              </div>

              <Link
                to={ROUTES.ATHLETE.PERFORMANCE_PROCESSING(performance.id)}
                className="rounded-xl border border-gray-200 px-5 py-3 text-sm font-bold text-gray-800 transition hover:border-[#F0600E] hover:text-[#F0600E]"
              >
                View Status
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}