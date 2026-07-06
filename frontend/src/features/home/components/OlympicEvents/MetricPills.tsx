type Props = {
  metrics: readonly string[];
};

export default function MetricPills({ metrics }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {metrics.map((metric) => (
        <span
          key={metric}
          className="rounded-full border border-orange-100 bg-[#FFF8F3] px-3 py-1.5 text-xs font-semibold text-[#F0600E]"
        >
          {metric}
        </span>
      ))}
    </div>
  );
}