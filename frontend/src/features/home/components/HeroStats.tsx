const stats = [
  { value: "4", label: "focused Olympic events" },
  { value: "AI", label: "posture & speed analysis" },
  { value: "1", label: "clip to start scouting" },
];

export default function HeroStats() {
  return (
    <div className="mt-12 grid max-w-xl grid-cols-3 gap-6 border-t border-border-default pt-7">
      {stats.map((stat) => (
        <div key={stat.label}>
          <div className="font-['JetBrains_Mono'] text-2xl font-semibold text-text-primary">
            {stat.value}
          </div>
          <div className="mt-1 text-xs leading-5 text-text-muted">
            {stat.label}
          </div>
        </div>
      ))}
    </div>
  );
}