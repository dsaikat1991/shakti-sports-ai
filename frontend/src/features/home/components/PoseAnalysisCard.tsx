const metrics = [
  {
    label: "Stride angle",
    value: "168°",
    className: "left-6 top-20",
    delay: "0s",
    distance: "6px",
  },
  {
    label: "100m split",
    value: "11.42s",
    className: "right-6 top-14",
    delay: ".8s",
    distance: "8px",
  },
  {
    label: "Ground contact",
    value: "0.09s",
    className: "left-8 bottom-28",
    delay: ".4s",
    distance: "7px",
  },
  {
    label: "Arm drive",
    value: "Balanced",
    className: "right-8 bottom-20",
    delay: "1.2s",
    distance: "5px",
  },
];

export default function PoseAnalysisCard() {
  return (
    <div className="relative h-130 overflow-hidden rounded-3xl border border-gray-200 bg-linear-to-b from-orange-50/70 via-white to-white shadow-2xl shadow-gray-200">
      <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4">
        <div className="flex items-center gap-2 font-['JetBrains_Mono'] text-xs font-semibold text-orange-700">
          <span className="h-2 w-2 rounded-full bg-[#F0600E]" />
          ANALYZING
        </div>

        <div className="font-['JetBrains_Mono'] text-xs text-gray-500">
          100m_sprint_trial_04.mp4
        </div>
      </div>

      <div className="relative h-107.5">
        <svg
          className="absolute inset-0 h-full w-full"
          viewBox="0 0 400 380"
          preserveAspectRatio="xMidYMid meet"
        >
          <line x1="0" y1="330" x2="400" y2="330" stroke="#E5E7EB" />
          <line x1="0" y1="300" x2="400" y2="300" stroke="#E5E7EB" />

          <g opacity="0.7">
            <line x1="205" y1="70" x2="200" y2="130" stroke="#111827" strokeWidth="2" />
            <line x1="200" y1="130" x2="170" y2="160" stroke="#111827" strokeWidth="2" />
            <line x1="200" y1="130" x2="235" y2="150" stroke="#111827" strokeWidth="2" />
            <line x1="170" y1="160" x2="150" y2="120" stroke="#111827" strokeWidth="2" />
            <line x1="235" y1="150" x2="260" y2="190" stroke="#111827" strokeWidth="2" />
            <line x1="200" y1="130" x2="196" y2="200" stroke="#111827" strokeWidth="2" />
            <line x1="196" y1="200" x2="150" y2="235" stroke="#111827" strokeWidth="2" />
            <line x1="150" y1="235" x2="160" y2="290" stroke="#111827" strokeWidth="2" />
            <line x1="196" y1="200" x2="245" y2="225" stroke="#111827" strokeWidth="2" />
            <line x1="245" y1="225" x2="225" y2="285" stroke="#111827" strokeWidth="2" />

            {[
              ["205", "70", "13"],
              ["200", "130", "4"],
              ["170", "160", "4"],
              ["150", "120", "4"],
              ["235", "150", "4"],
              ["260", "190", "4"],
              ["196", "200", "4"],
              ["150", "235", "4"],
              ["160", "290", "4"],
              ["245", "225", "4"],
              ["225", "285", "4"],
            ].map(([cx, cy, r]) => (
              <circle
                key={`${cx}-${cy}`}
                cx={cx}
                cy={cy}
                r={r}
                fill="#F0600E"
              />
            ))}
          </g>
        </svg>

        {metrics.map((metric) => (
          <div
            key={metric.label}
            style={
              {
                animationDelay: metric.delay,
                "--float-distance": metric.distance,
              } as React.CSSProperties
            }
            className={`floating-card absolute rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-xl shadow-gray-200/70 will-change-transform ${metric.className}`}
          >
            <div className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-wide text-gray-500">
              {metric.label}
            </div>

            <div className="mt-1 font-['JetBrains_Mono'] text-sm font-semibold text-green-700">
              {metric.value}
            </div>
          </div>
        ))}
      </div>

      <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between border-t border-gray-200 bg-white/90 px-5 py-4">
        <div className="font-['JetBrains_Mono'] text-xs font-semibold text-green-700">
          FORM SCORE 8.7/10
        </div>

        <div className="h-2 w-24 overflow-hidden rounded-full bg-green-100">
          <div className="h-full w-[87%] bg-green-700" />
        </div>
      </div>
    </div>
  );
}