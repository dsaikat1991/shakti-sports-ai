import type { eventData } from "./data";

type EventItem = (typeof eventData)[number];

type Props = {
  events: readonly EventItem[];
  activeId: EventItem["id"];
  onChange: (id: EventItem["id"]) => void;
};

export default function EventTabs({ events, activeId, onChange }: Props) {
  return (
    <div className="mt-10 flex flex-wrap gap-3">
      {events.map((event) => {
        const isActive = event.id === activeId;

        return (
          <button
            key={event.id}
            onClick={() => onChange(event.id)}
            className={`cursor-pointer rounded-2xl border px-5 py-3 text-left transition duration-300 ${
              isActive
                ? "border-[#F0600E] bg-[#FFF8F3] text-[#F0600E] shadow-lg shadow-orange-100"
                : "border-gray-200 bg-white text-gray-600 hover:border-orange-300 hover:text-[#F0600E]"
            }`}
          >
            <div className="text-sm font-bold">{event.name}</div>
            <div className="mt-1 font-['JetBrains_Mono'] text-[10px] uppercase tracking-widest opacity-70">
              {event.label}
            </div>
          </button>
        );
      })}
    </div>
  );
}