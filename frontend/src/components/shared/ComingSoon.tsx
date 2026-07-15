import { Construction } from "lucide-react";
import { Link } from "react-router-dom";
import { ROUTES } from "../../constants/routes";

type ComingSoonAction =
  | { type: "link"; to: string; label: string }
  | { type: "button"; onClick: () => void; label: string };

export default function ComingSoon({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ComingSoonAction;
}) {
  const resolvedAction: ComingSoonAction = action ?? {
    type: "link",
    to: ROUTES.ATHLETE.HOME,
    label: "Back to Dashboard",
  };

  return (
    <div className="mx-auto max-w-2xl rounded-4xl border border-gray-200 bg-white p-10 text-center shadow-sm">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-orange-100 text-[#F0600E]">
        <Construction className="h-6 w-6" />
      </div>

      <p className="mt-4 font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
        Coming Soon
      </p>

      <h1 className="mt-4 font-['Anton'] text-4xl uppercase leading-none text-gray-950">
        {title}
      </h1>

      <p className="mx-auto mt-4 max-w-md text-base leading-7 text-gray-600">
        {description}
      </p>

      {resolvedAction.type === "link" ? (
        <Link
          to={resolvedAction.to}
          className="mt-8 inline-flex rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
        >
          {resolvedAction.label}
        </Link>
      ) : (
        <button
          type="button"
          onClick={resolvedAction.onClick}
          className="mt-8 cursor-pointer rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
        >
          {resolvedAction.label}
        </button>
      )}
    </div>
  );
}
