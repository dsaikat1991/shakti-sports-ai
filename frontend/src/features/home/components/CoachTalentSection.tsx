import { Filter, Play, Search, Star } from "lucide-react";

const athletes = [
  {
    name: "Riya Sharma",
    age: "16",
    event: "100m Sprint",
    state: "Haryana",
    score: "9.2",
  },
  {
    name: "Arjun Singh",
    age: "18",
    event: "Long Jump",
    state: "Punjab",
    score: "8.9",
  },
  {
    name: "Rahul Das",
    age: "17",
    event: "110m Hurdles",
    state: "West Bengal",
    score: "8.7",
  },
];

const filters = ["Event", "Age", "State", "Score"];

export default function CoachTalentSection() {
  return (
    <section id="coaches" className="bg-gray-950 py-24 text-white">
      <div className="mx-auto grid max-w-7xl items-center gap-14 px-6 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
        <div>
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-orange-400">
            For Coaches, Academies & Talent Scouts
          </p>

          <h2 className="mt-4 font-['Anton'] text-4xl uppercase leading-none tracking-tight md:text-6xl">
            Great Talent
            <span className="block text-[#F0600E]">Deserves Great Visibility</span>
          </h2>

          <p className="mt-6 max-w-xl text-lg leading-8 text-white/65">
            Search athletes across districts, compare AI-generated movement
            reports, watch source videos, and build shortlists based on
            objective performance data.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {[
              "Search by event, age, state and score",
              "Compare athletes side by side",
              "Watch original training videos",
              "Build trial-ready shortlists",
            ].map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-white/10 bg-white/4 p-4 text-sm font-semibold text-white/80"
              >
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/4 p-5 shadow-2xl shadow-black/40">
          <div className="rounded-2xl bg-white p-5 text-gray-950">
            <div className="flex items-center justify-between border-b border-gray-200 pb-4">
              <div>
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-widest text-gray-500">
                  Coach Dashboard
                </p>
                <h3 className="mt-1 text-xl font-bold">Athlete Search</h3>
              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-50">
                <Search className="h-5 w-5 text-[#F0600E]" />
              </div>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-4">
              {filters.map((filter) => (
                <div
                  key={filter}
                  className="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-xs font-semibold text-gray-600"
                >
                  {filter}
                  <Filter className="h-3.5 w-3.5 text-gray-400" />
                </div>
              ))}
            </div>

            <div className="mt-5 space-y-3">
              {athletes.map((athlete) => (
                <div
                  key={athlete.name}
                  className="grid grid-cols-[1fr_auto] items-center gap-4 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"
                >
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="font-bold text-gray-950">
                        {athlete.name}
                      </h4>
                      <span className="rounded-full bg-green-100 px-2.5 py-1 text-[11px] font-bold text-green-700">
                        {athlete.score}
                      </span>
                    </div>

                    <p className="mt-1 text-sm text-gray-500">
                      Age {athlete.age} · {athlete.event} · {athlete.state}
                    </p>
                  </div>

                  <button className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-full bg-gray-950 text-white transition hover:bg-[#F0600E]">
                    <Play className="h-4 w-4 fill-current" />
                  </button>
                </div>
              ))}
            </div>

            <div className="mt-5 rounded-2xl bg-gray-950 p-4 text-white">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#F0600E]">
                  <Star className="h-5 w-5 fill-current" />
                </div>

                <div>
                  <p className="text-sm font-bold">Shortlist Ready</p>
                  <p className="text-xs text-white/50">
                    12 athletes match your sprint benchmark.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}