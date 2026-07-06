const journeySteps = [
  {
    step: "01",
    title: "Upload",
    description: "Record a sprint or jump clip and upload it from your phone.",
  },
  {
    step: "02",
    title: "AI Analysis",
    description: "Shakti reads posture, speed, timing and movement quality.",
  },
  {
    step: "03",
    title: "Build Profile",
    description: "Every report strengthens your athlete profile over time.",
  },
];

export default function AthleteJourney() {
  return (
    <section id="athletes" className="bg-[#FFF8F3] py-16 lg:py-20">
      <div className="mx-auto grid max-w-7xl items-center gap-10 px-6 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
        <div>
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-orange-600">
            For Athletes
          </p>

          <h2 className="mt-3 font-['Anton'] text-4xl uppercase leading-[0.92] tracking-tight text-gray-950 md:text-5xl">
            Train anywhere.
            <span className="block text-[#F0600E]">Get discovered everywhere.</span>
          </h2>

          <p className="mt-4 max-w-xl text-base leading-7 text-gray-600">
            Your talent should not depend on who sees you at one trial. Upload
            training videos, track progress, and become visible to coaches
            looking for athletes like you.
          </p>

          <div className="mt-7 space-y-3">
            {journeySteps.map((item) => (
              <div
                key={item.step}
                className="group flex gap-4 rounded-2xl border border-orange-100 bg-white/80 px-5 py-4 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-orange-300 hover:bg-white hover:shadow-xl hover:shadow-orange-100"
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#F0600E] font-['JetBrains_Mono'] text-[11px] font-bold text-white">
                  {item.step}
                </div>

                <div>
                  <h3 className="text-base font-bold text-gray-950">
                    {item.title}
                  </h3>
                  <p className="mt-1 text-sm leading-5 text-gray-600">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <p className="mt-5 text-sm font-semibold text-[#F0600E]">
            ...and get discovered by coaches across India.
          </p>
        </div>

        <div className="rounded-4xl border border-orange-100 bg-white p-5 shadow-2xl shadow-orange-100">
          <div className="rounded-3xl bg-gray-950 p-5 text-white">
            <div className="flex items-start justify-between border-b border-white/10 pb-4">
              <div>
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-widest text-orange-400">
                  Athlete Profile
                </p>
                <h3 className="mt-1.5 text-2xl font-bold">Aryan Roy</h3>
                <p className="mt-1 text-sm text-white/50">
                  Age 17 · 100m Sprint · West Bengal
                </p>
              </div>

              <div className="rounded-full bg-green-400/10 px-3 py-1.5 text-xs font-bold text-green-300">
                Visible to Coaches
              </div>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl bg-white/6 p-3">
                <p className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-widest text-white/40">
                  AI Score
                </p>
                <p className="mt-2 font-['Anton'] text-4xl text-[#F0600E]">
                  8.9
                </p>
              </div>

              <div className="rounded-2xl bg-white/6 p-3">
                <p className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-widest text-white/40">
                  Coach Views
                </p>
                <p className="mt-2 font-['Anton'] text-4xl">24</p>
              </div>

              <div className="rounded-2xl bg-white/6 p-3">
                <p className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-widest text-white/40">
                  Invites
                </p>
                <p className="mt-2 font-['Anton'] text-4xl">3</p>
              </div>
            </div>

            <div className="mt-4 rounded-2xl bg-white/6 p-4">
              <div className="mb-3 flex items-center justify-between">
                <p className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-widest text-white/40">
                  Weekly Progress
                </p>
                <p className="text-xs font-semibold text-green-300">
                  +14% improvement
                </p>
              </div>

              <svg viewBox="0 0 420 120" className="h-24 w-full">
                <path
                  d="M20 96 C70 86, 90 78, 125 72 C160 66, 175 48, 210 54 C260 61, 275 33, 315 28 C350 23, 370 19, 400 15"
                  fill="none"
                  stroke="#F0600E"
                  strokeWidth="5"
                  strokeLinecap="round"
                />
                {[20, 125, 210, 315, 400].map((x, index) => (
                  <circle
                    key={x}
                    cx={x}
                    cy={[96, 72, 54, 28, 15][index]}
                    r="5"
                    fill="#F0600E"
                  />
                ))}
              </svg>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              {["Fast Starter", "Top 10%", "Coach Pick"].map((badge) => (
                <div
                  key={badge}
                  className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-center text-xs font-bold text-white/80 transition hover:border-orange-400/50 hover:text-white"
                >
                  {badge}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}