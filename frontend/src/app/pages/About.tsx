import Container from "../../components/ui/Container";

const beliefs = [
  {
    title: "Performance Over Perception",
    description:
      "Talent should be measured through objective performance and scientific analysis rather than assumptions or limited exposure.",
  },
  {
    title: "Technology Should Democratize Opportunity",
    description:
      "Elite sports science should not be available only to national camps and professional academies. Every athlete deserves access to modern performance analysis.",
  },
  {
    title: "Data Should Build Trust",
    description:
      "We believe athletes deserve honest feedback. If a recording is unsuitable for reliable analysis, our platform explains why rather than producing misleading results.",
  },
  {
    title: "Continuous Growth",
    description:
      "Athletic development is a journey. Every upload, every training session, and every competition contributes to a deeper understanding of an athlete's progress.",
  },
];

const audiences = [
  {
    title: "Athletes",
    description:
      "Receive detailed AI-powered performance analysis, identify strengths and weaknesses, and track long-term improvement.",
  },
  {
    title: "Coaches",
    description:
      "Understand athlete biomechanics, monitor development, and make evidence-based training decisions.",
  },
  {
    title: "Academies",
    description:
      "Evaluate athletes consistently using objective performance metrics.",
  },
  {
    title: "Talent Scouts",
    description:
      "Discover promising athletes based on measurable performance rather than limited visibility.",
  },
];

export default function About() {
  return (
    <div className="bg-[#FAFAF7] py-20">
      <Container className="max-w-4xl">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
          About Shakti Sports AI
        </p>

        <h1 className="mt-4 font-['Anton'] text-4xl uppercase leading-none text-gray-950 md:text-6xl">
          Discovering India's Next Generation of Champions
        </h1>

        <div className="mt-8 space-y-5 text-base leading-7 text-gray-600">
          <p>
            India is home to millions of talented young athletes. Yet every
            year, countless promising players go unnoticed — not because
            they lack potential, but because they lack access to
            professional coaching, scientific analysis, and opportunities to
            be seen.
          </p>

          <p className="font-bold text-gray-950">
            Shakti Sports AI was created to change that.
          </p>

          <p>
            We are building an AI-powered athlete intelligence platform that
            helps athletes, coaches, academies, and talent scouts make
            data-driven decisions through advanced biomechanical analysis
            and performance insights.
          </p>

          <p>
            Using computer vision and artificial intelligence, athletes can
            upload a simple training video recorded on a smartphone. Our
            platform analyses movement patterns, sprint mechanics, joint
            kinematics, stride characteristics, recording quality, and other
            performance indicators to generate objective insights that
            support training and talent identification.
          </p>

          <p>But our vision extends far beyond biomechanics.</p>

          <p>
            We believe every athlete deserves to be evaluated by
            performance — not geography, financial background, or access to
            elite facilities.
          </p>

          <p>
            Our goal is to create a transparent ecosystem where talent can
            be discovered anywhere in India.
          </p>

          <p>
            Whether you're an aspiring athlete looking to improve, a coach
            developing future champions, or a scout searching for
            exceptional talent, Shakti Sports AI is built to support your
            journey.
          </p>
        </div>

        <div className="mt-16">
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
            What We Believe
          </p>

          <div className="mt-6 grid gap-5 sm:grid-cols-2">
            {beliefs.map((belief) => (
              <div
                key={belief.title}
                className="rounded-3xl border border-gray-200 bg-white p-6"
              >
                <h3 className="text-lg font-bold text-gray-950">
                  {belief.title}
                </h3>
                <p className="mt-2 text-sm leading-6 text-gray-600">
                  {belief.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16">
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
            Built for the Entire Sporting Ecosystem
          </p>

          <div className="mt-6 grid gap-5 sm:grid-cols-2">
            {audiences.map((audience) => (
              <div
                key={audience.title}
                className="rounded-3xl border border-gray-200 bg-white p-6"
              >
                <h3 className="text-lg font-bold text-gray-950">
                  {audience.title}
                </h3>
                <p className="mt-2 text-sm leading-6 text-gray-600">
                  {audience.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </Container>
    </div>
  );
}
