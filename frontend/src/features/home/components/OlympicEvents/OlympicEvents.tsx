import { useState } from "react";
import EventPreview from "./EventPreview";
import EventTabs from "./EventTabs";
import MetricPills from "./MetricPills";
import RecordingGuide from "./RecordingGuide";
import { eventData } from "./data";

type EventId = (typeof eventData)[number]["id"];

export default function OlympicEvents() {
  const [activeId, setActiveId] = useState<EventId>("sprint");
  const activeEvent =
    eventData.find((event) => event.id === activeId) ?? eventData[0];

  return (
    <section id="sports" className="bg-surface-canvas py-20 lg:py-24">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="max-w-3xl">
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
            Shakti Performance Engine
          </p>

          <h2 className="mt-3 text-2xl font-bold text-text-primary md:text-3xl">
            Record once.
            <span className="block text-brand-action">Analyze right.</span>
          </h2>

          <p className="mt-4 max-w-2xl text-base leading-7 text-text-secondary">
            Follow the recommended recording setup for each event to receive the
            most accurate AI analysis.
          </p>
        </div>

        <EventTabs
          events={eventData}
          activeId={activeId}
          onChange={setActiveId}
        />

        <div className="mt-10 grid items-start gap-8 lg:grid-cols-[0.95fr_1.05fr]">
          <div>
            <div className="rounded-4xl border border-border-default bg-surface-card p-6 shadow-xl shadow-border-default/60">
              <div className="mb-5 flex items-center justify-between border-b border-border-default pb-5">
                <div>
                  <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-widest text-text-disabled">
                    Recording Guide
                  </p>
                  <h3 className="mt-1 text-2xl font-bold text-text-primary">
                    {activeEvent.name}
                  </h3>
                </div>

                <span className="rounded-full bg-brand-action-soft px-3 py-1.5 text-xs font-bold text-brand-action">
                  {activeEvent.label}
                </span>
              </div>

              <RecordingGuide
                camera={activeEvent.camera}
                distance={activeEvent.distance}
                fps={activeEvent.fps}
                duration={activeEvent.duration}
                lighting={activeEvent.lighting}
              />

              <div className="mt-6">
                <p className="mb-3 font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-text-disabled">
                  AI Measures
                </p>

                <MetricPills metrics={activeEvent.metrics} />
              </div>
            </div>

            
          </div>

          <EventPreview
            quality={activeEvent.quality}
            good={activeEvent.good}
            poor={activeEvent.poor}
          />
        </div>
      </div>
    </section>
  );
}