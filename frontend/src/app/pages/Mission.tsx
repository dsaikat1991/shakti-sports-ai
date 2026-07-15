import Container from "../../components/ui/Container";

const visionItems = [
  "Identifies emerging talent from every corner of India.",
  "Tracks athletic development over time through AI-powered digital performance profiles.",
  "Provides coaches and academies with actionable performance insights.",
  "Supports evidence-based athlete selection.",
  "Helps athletes understand their strengths, improve weaknesses, and unlock their full potential.",
  "Contributes to India's pursuit of excellence in national and international competitions.",
];

export default function Mission() {
  return (
    <div className="bg-[#FAFAF7] py-20">
      <Container className="max-w-4xl">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
          Our Mission
        </p>

        <h1 className="mt-4 font-['Anton'] text-4xl uppercase leading-none text-gray-950 md:text-6xl">
          Empower Every Athlete. Discover Every Champion.
        </h1>

        <div className="mt-8 space-y-5 text-base leading-7 text-gray-600">
          <p>
            Our mission is to build India's most trusted AI-powered athlete
            intelligence platform — one that gives every athlete an equal
            opportunity to be discovered, developed, and celebrated.
          </p>

          <p>
            We envision a future where talent is no longer limited by
            geography, infrastructure, or opportunity.
          </p>

          <p>
            Through responsible artificial intelligence, computer vision,
            and sports science, we aim to make professional-level
            performance analysis accessible to athletes at every stage of
            their journey.
          </p>

          <p>
            We are committed to helping athletes improve through objective
            insights, supporting coaches with meaningful data, enabling
            scouts to identify emerging talent, and strengthening India's
            sporting ecosystem through technology.
          </p>
        </div>

        <div className="mt-16">
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
            Our Long-Term Vision
          </p>

          <p className="mt-4 text-base leading-7 text-gray-600">
            We believe the future of sports is driven by intelligence as
            much as effort. Our long-term vision is to build a national
            athlete intelligence network that:
          </p>

          <ul className="mt-6 space-y-3">
            {visionItems.map((item) => (
              <li
                key={item}
                className="flex items-start gap-3 rounded-2xl border border-gray-200 bg-white p-4 text-sm leading-6 text-gray-700"
              >
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#F0600E]" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-16 rounded-3xl border border-orange-200 bg-[#FFF8F3] p-8">
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
            Our Promise
          </p>

          <div className="mt-4 space-y-4 text-base leading-7 text-gray-700">
            <p>
              Every recommendation we generate is grounded in measurable
              data.
            </p>
            <p>When our AI is confident, we explain why.</p>
            <p>
              When the available data is insufficient, we say so clearly.
            </p>
            <p>
              We believe trust is earned through transparency, scientific
              rigor, and continuous improvement — not by claiming certainty
              where it does not exist.
            </p>
          </div>
        </div>

        <div className="mt-16 text-center">
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-gray-400">
            Our Tagline
          </p>

          <p className="mt-4 font-['Anton'] text-2xl uppercase leading-tight text-gray-950 md:text-3xl">
            Discovering Talent. Empowering Performance. Building India's
            Champions.
          </p>
        </div>
      </Container>
    </div>
  );
}
