type Props = {
  metrics: readonly string[];
};

export default function MetricPills({ metrics }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {metrics.map((metric) => (
        <span
          key={metric}
          className="rounded-full border border-brand-action-soft bg-surface-sunken px-3 py-1.5 text-xs font-semibold text-brand-action"
        >
          {metric}
        </span>
      ))}
    </div>
  );
}