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
    icon: "bg-orange-50 text-[#F0600E]",
    border: "hover:border-[#F0600E] hover:shadow-orange-100",
  },
  green: {
    icon: "bg-green-50 text-green-700",
    border: "hover:border-green-600 hover:shadow-green-100",
  },
  blue: {
    icon: "bg-blue-50 text-blue-700",
    border: "hover:border-blue-600 hover:shadow-blue-100",
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
      className={`group w-full cursor-pointer rounded-4xl border border-gray-200 bg-white p-7 text-left shadow-xl shadow-gray-200/50 transition duration-300 hover:-translate-y-1 hover:shadow-2xl ${styles.border}`}
    >
      <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${styles.icon}`}>
        <Icon className="h-7 w-7" />
      </div>

      <h3 className="mt-6 font-['Anton'] text-3xl uppercase text-gray-950">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-gray-600">
        {description}
      </p>

      <div className="mt-6 space-y-3">
        {points.map((point) => (
          <p key={point} className="text-sm font-semibold text-gray-800">
            — {point}
          </p>
        ))}
      </div>

      <p className="mt-7 text-sm font-bold text-gray-950 group-hover:text-[#F0600E]">
        Continue →
      </p>
    </button>
  );
}