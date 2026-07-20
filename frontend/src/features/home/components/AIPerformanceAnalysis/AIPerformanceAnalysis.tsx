import { useState } from "react";
import { analysisEvents } from "./data";

export default function AIPerformanceAnalysis() {
  const [activeIndex, setActiveIndex] = useState(0);
  const active = analysisEvents[activeIndex];

  return (
    <section className="bg-surface-canvas py-20">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="max-w-3xl">
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
            AI Performance Analysis
          </p>

          <h2 className="mt-4 text-2xl font-bold text-text-primary md:text-3xl">
            We don't just watch videos.
            <span className="block text-brand-action">We understand movement.</span>
          </h2>
        </div>

        <div className="mt-10 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="rounded-3xl border border-border-default bg-surface-card p-6 shadow-xl shadow-border-default/60">
            <div className="flex items-center justify-between border-b border-border-default pb-4">
              <div>
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-widest text-text-muted">
                  Active Event
                </p>
                <h3 className="mt-1 text-2xl font-bold text-text-primary">
                  {active.name}
                </h3>
              </div>

              <div className="rounded-full bg-success-progress-soft px-4 py-2 font-['JetBrains_Mono'] text-xs font-semibold text-success-progress-hover">
                {active.score}
              </div>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              {active.metrics.map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-2xl border border-border-divider bg-surface-sunken px-4 py-3"
                >
                  <span className="block text-xs font-medium text-text-muted">
                    {label}
                  </span>
                  <span className="mt-1 block font-['JetBrains_Mono'] text-sm font-semibold text-text-primary">
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-border-default bg-gray-950 p-6 text-white shadow-2xl shadow-border-default">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <div>
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-widest text-orange-400">
                  Movement Intelligence
                </p>
                <h3 className="mt-1 text-lg font-semibold">
                  {active.summary}
                </h3>
              </div>

              <p className="font-['JetBrains_Mono'] text-xs text-white/50">
                MODEL VIEW
              </p>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/4 p-5">
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-widest text-white/40">
                  Movement Score
                </p>
                <p className="mt-3 text-5xl font-bold text-brand-action">
                  {active.score}
                </p>
                <p className="mt-3 text-sm leading-6 text-white/60">
                  Composite score generated from posture, timing, movement
                  symmetry and event-specific mechanics.
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/4 p-5">
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-widest text-white/40">
                  AI Scan Layers
                </p>

                <div className="mt-5 space-y-3">
                  {["Pose", "Timing", "Symmetry", "Event mechanics"].map(
                    (item, index) => (
                      <div key={item}>
                        <div className="mb-1 flex justify-between text-xs">
                          <span className="text-white/60">{item}</span>
                          <span className="text-white/80">
                            {92 - index * 4}%
                          </span>
                        </div>
                        <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
                          <div
                            className="h-full rounded-full bg-brand-action"
                            style={{ width: `${92 - index * 4}%` }}
                          />
                        </div>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </div>

            <div className="mt-4 rounded-2xl border border-white/10 bg-white/4 p-5">
              <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-widest text-white/40">
                Coach-ready output
              </p>

              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                {["Report", "Benchmark", "Shortlist"].map((item) => (
                  <div
                    key={item}
                    className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm font-semibold text-white/80"
                  >
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          {analysisEvents.map((event, index) => (
            <button
              key={event.id}
              onClick={() => setActiveIndex(index)}
              className={`cursor-pointer rounded-2xl border p-5 text-left transition duration-300 ${
                active.id === event.id
                  ? "border-brand-action bg-surface-card shadow-xl shadow-brand-action-soft"
                  : "border-border-default bg-surface-card/70 hover:border-brand-action-soft hover:bg-surface-card"
              }`}
            >
              <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-widest text-text-muted">
                {event.label}
              </p>
              <h4 className="mt-3 text-xl font-bold text-text-primary">
                {event.name}
              </h4>
              <p className="mt-2 text-sm text-text-muted">{event.summary}</p>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}