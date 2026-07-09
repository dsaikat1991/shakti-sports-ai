import { CheckCircle2, Loader2 } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { ROUTES } from "../../../constants/routes";

export default function PerformanceProcessing() {
  const { performanceId } = useParams();

  return (
    <div className="mx-auto max-w-3xl rounded-4xl border border-gray-200 bg-white p-8 text-center shadow-2xl shadow-gray-200/70">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-green-100 text-green-700">
        <CheckCircle2 className="h-8 w-8" />
      </div>

      <p className="mt-6 font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
        Upload Complete
      </p>

      <h1 className="mt-4 font-['Anton'] text-5xl uppercase leading-none text-gray-950">
        Performance saved.
      </h1>

      <p className="mx-auto mt-4 max-w-xl text-base leading-7 text-gray-600">
        Shakti Motion Intelligence™ will analyze this recording in the next
        stage. For now, your performance has been securely saved.
      </p>

      <div className="mx-auto mt-8 max-w-md rounded-3xl border border-orange-200 bg-[#FFF8F3] p-5">
        <div className="flex items-center justify-center gap-3 text-sm font-bold text-gray-950">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Preparing AI analysis pipeline
        </div>

        <p className="mt-2 break-all font-['JetBrains_Mono'] text-[10px] uppercase tracking-widest text-gray-400">
          ID: {performanceId}
        </p>
      </div>

      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Link
          to={ROUTES.ATHLETE.HOME}
          className="rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
        >
          Go to Dashboard
        </Link>

        <Link
          to={ROUTES.ATHLETE.NEW_PERFORMANCE}
          className="rounded-xl border border-gray-300 px-5 py-3 text-sm font-bold text-gray-800 transition hover:border-[#F0600E] hover:text-[#F0600E]"
        >
          Start Another Performance
        </Link>
      </div>
    </div>
  );
}