const analysisPoints = [
  "Frame-by-frame posture mapping",
  "Speed and timing indicators",
  "Stride and jump mechanics",
  "Coach-ready performance report",
];

export default function AIAnalysis() {
  return (
    <section id="athletes" className="bg-gray-50 py-24">
      <div className="mx-auto grid max-w-7xl items-center gap-14 px-6 lg:grid-cols-2 lg:px-8">
        <div>
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-green-700">
            AI Analysis
          </p>

          <h2 className="mt-4 font-['Anton'] text-4xl uppercase leading-none tracking-tight text-gray-950 md:text-5xl">
            Turn one training clip into useful performance data.
          </h2>

          <p className="mt-6 max-w-xl text-lg leading-8 text-gray-600">
            Athletes do not need expensive sensors or lab cameras. Shakti Sports
            AI starts with a simple phone video and converts movement into
            measurable insights.
          </p>

          <div className="mt-8 grid gap-4">
            {analysisPoints.map((point) => (
              <div
                key={point}
                className="flex items-center gap-3 rounded-2xl border border-gray-200 bg-white px-5 py-4 shadow-sm"
              >
                <span className="h-2.5 w-2.5 rotate-45 rounded-sm bg-[#F0600E]" />
                <span className="text-sm font-semibold text-gray-800">
                  {point}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-2xl shadow-gray-200">
          <div className="rounded-2xl bg-gray-950 p-5 text-white">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <p className="font-['JetBrains_Mono'] text-xs text-orange-400">
                ATHLETE REPORT
              </p>
              <p className="font-['JetBrains_Mono'] text-xs text-white/50">
                READY
              </p>
            </div>

            <div className="mt-6 space-y-5">
              {[
                ["Acceleration", "8.4"],
                ["Posture Control", "8.9"],
                ["Stride Efficiency", "8.1"],
                ["Scout Readiness", "High"],
              ].map(([label, value]) => (
                <div key={label}>
                  <div className="mb-2 flex justify-between text-sm">
                    <span className="text-white/70">{label}</span>
                    <span className="font-semibold text-white">{value}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-white/10">
                    <div className="h-full w-[82%] rounded-full bg-[#F0600E]" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}