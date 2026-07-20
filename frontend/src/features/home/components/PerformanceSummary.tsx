const performanceCards = [
  {
    title: "Sprint Analysis",
    description: "Measure stride angle, ground contact, cadence, acceleration and speed.",
    value: "100m / 200m",
  },
  {
    title: "Hurdle Mechanics",
    description: "Track lead leg, trail leg, clearance rhythm and landing balance.",
    value: "100m / 110m",
  },
  {
    title: "Long Jump",
    description: "Analyze run-up speed, take-off angle, flight form and landing efficiency.",
    value: "Jump Events",
  },
  {
    title: "High Jump",
    description: "Review curve run, take-off foot, hip clearance and landing safety.",
    value: "Jump Events",
  },
];

export default function PerformanceSummary() {
  return (
    <section id="platform" className="bg-surface-card py-20">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mb-10 max-w-2xl">
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
            Performance Summary
          </p>

          <h2 className="mt-4 text-2xl font-bold text-text-primary md:text-3xl">
            Focused on events AI can measure well.
          </h2>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {performanceCards.map((card) => (
            <div
              key={card.title}
              className="rounded-3xl border border-border-default bg-surface-card p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-border-default/70"
            >
              <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-wider text-success-progress-hover">
                {card.value}
              </p>

              <h3 className="mt-5 text-xl font-bold text-text-primary">
                {card.title}
              </h3>

              <p className="mt-4 text-sm leading-6 text-text-secondary">
                {card.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}