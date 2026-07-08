import { ArrowRight, Eye, Medal, Plus, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";

export default function AthleteHome() {
  return (
    <div className="mx-auto max-w-6xl">
      <div>
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
          Shakti Motion Intelligence™
        </p>

        <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
          Ready for today’s performance?
        </h1>

        <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
          Start a new performance, track your progress, and build a profile that
          coaches can discover.
        </p>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Link
  to="/console/athlete/performances/new"
  className="group block rounded-4xl border border-orange-200 bg-[#FFF8F3] p-8 shadow-xl shadow-orange-100 transition duration-300 hover:-translate-y-1 hover:border-[#F0600E]"
>
  <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#F0600E] text-white">
    <Plus className="h-7 w-7" />
  </div>

  <h2 className="mt-8 font-['Anton'] text-4xl uppercase leading-none text-gray-950">
    Start New Performance
  </h2>

  <p className="mt-4 max-w-xl text-sm leading-6 text-gray-600">
    Choose your event, upload your recording, and let Shakti generate a
    performance report.
  </p>

  <div className="mt-8 flex items-center gap-2 text-sm font-black text-[#F0600E]">
    Begin Analysis

    <ArrowRight className="h-4 w-4 transition duration-300 group-hover:translate-x-1" />
  </div>
</Link>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-xl shadow-gray-200/70">
          <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
            Latest Performance
          </p>

          <h3 className="mt-4 text-2xl font-bold text-gray-950">
            Sprint Practice
          </h3>

          <p className="mt-1 text-sm text-gray-500">Yesterday · 100m Sprint</p>

          <div className="mt-6 flex items-end justify-between">
            <div>
              <p className="text-sm font-semibold text-gray-500">
                Performance Score
              </p>
              <p className="mt-2 font-['Anton'] text-6xl text-[#F0600E]">
                8.9
              </p>
            </div>

            <div className="rounded-full bg-green-100 px-3 py-1.5 text-xs font-bold text-green-700">
              +0.4 improved
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <TrendingUp className="h-5 w-5 text-[#F0600E]" />
            <h3 className="font-bold text-gray-950">Weekly Progress</h3>
          </div>

          <svg viewBox="0 0 360 130" className="mt-6 h-32 w-full">
            <path
              d="M10 105 C55 90, 78 88, 105 72 C145 48, 174 70, 210 50 C250 28, 300 34, 350 18"
              fill="none"
              stroke="#F0600E"
              strokeWidth="5"
              strokeLinecap="round"
            />
          </svg>
        </div>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <Eye className="h-5 w-5 text-green-700" />
            <h3 className="font-bold text-gray-950">Coach Activity</h3>
          </div>

          <p className="mt-6 font-['Anton'] text-5xl text-gray-950">2</p>
          <p className="mt-2 text-sm text-gray-500">coaches viewed your profile</p>
        </div>

        <div className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <Medal className="h-5 w-5 text-[#F0600E]" />
            <h3 className="font-bold text-gray-950">Personal Best</h3>
          </div>

          <p className="mt-6 font-['Anton'] text-5xl text-gray-950">11.31s</p>
          <p className="mt-2 text-sm text-gray-500">100m sprint benchmark</p>
        </div>
      </div>
    </div>
  );
}