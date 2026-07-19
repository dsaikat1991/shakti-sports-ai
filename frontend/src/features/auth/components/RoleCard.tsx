import type { LucideIcon } from "lucide-react";

type Props = {
  icon: LucideIcon;
  title: string;
  description: string;
  points: string[];
  accent: "orange" | "green" | "blue";
  onClick: () => void;
};

const accentStyles = {
  orange: {
    icon: "bg-brand-action-soft text-brand-action",
    border: "hover:border-brand-action hover:shadow-brand-action-soft",
  },
  green: {
    icon: "bg-success-progress-tint text-success-progress-hover",
    border: "hover:border-success-progress hover:shadow-success-progress-soft",
  },
  blue: {
    icon: "bg-info-insight-tint text-info-insight-hover",
    border: "hover:border-info-insight hover:shadow-info-insight-soft",
  },
};

export default function RoleCard({
  icon: Icon,
  title,
  description,
  points,
  accent,
  onClick,
}: Props) {
  const styles = accentStyles[accent];

  return (
    <button
      type="button"
      onClick={onClick}
      className={`group w-full cursor-pointer rounded-4xl border border-border-default bg-surface-card p-7 text-left shadow-xl shadow-border-default/50 transition duration-300 hover:-translate-y-1 hover:shadow-2xl ${styles.border}`}
    >
      <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${styles.icon}`}>
        <Icon className="h-7 w-7" />
      </div>

      <h3 className="mt-6 font-['Anton'] text-3xl uppercase text-text-primary">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-text-secondary">
        {description}
      </p>

      <div className="mt-6 space-y-3">
        {points.map((point) => (
          <p key={point} className="text-sm font-semibold text-text-primary">
            — {point}
          </p>
        ))}
      </div>

      <p className="mt-7 text-sm font-bold text-text-primary group-hover:text-brand-action">
        Continue →
      </p>
    </button>
  );
}