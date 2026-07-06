import { comingSoonEvents } from "./data";

export default function ComingSoon() {
  return (
    <div className="mt-10 rounded-3xl border border-gray-200 bg-white p-5">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
        Coming Soon
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {comingSoonEvents.map((event) => (
          <span
            key={event}
            className="rounded-full bg-gray-100 px-3 py-1.5 text-xs font-semibold text-gray-500"
          >
            {event}
          </span>
        ))}
      </div>
    </div>
  );
}