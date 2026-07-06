import { BarChart3, Medal, ScanLine, Smartphone, Upload } from "lucide-react";

const steps = [
  {
    icon: Smartphone,
    title: "Record",
    description: "Capture a sprint, hurdle, long jump, or high jump clip on any phone.",
  },
  {
    icon: Upload,
    title: "Upload",
    description: "Upload the training video directly to Shakti Sports AI.",
  },
  {
    icon: ScanLine,
    title: "AI Scan",
    description: "Our model reads posture, timing, speed, angles, and movement quality.",
  },
  {
    icon: BarChart3,
    title: "Report",
    description: "Athletes receive clear metrics, scores, and improvement signals.",
  },
  {
    icon: Medal,
    title: "Get Discovered",
    description: "Verified coaches and scouts can find athletes by event and performance.",
  },
];

export default function HowItWorks() {
  return (
    <section id="platform" className="bg-white py-24">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="max-w-3xl">
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-orange-600">
            How it works
          </p>

          <h2 className="mt-4 font-['Anton'] text-4xl uppercase leading-none tracking-tight text-gray-950 md:text-5xl">
            One clip. Five steps to getting discovered.
          </h2>
        </div>

        <div className="relative mt-16">
          <div className="absolute left-0 right-0 top-8 hidden h-px bg-gray-200 lg:block" />

          <div className="grid gap-5 lg:grid-cols-5">
            {steps.map((step, index) => {
              const Icon = step.icon;

              return (
                <div
                  key={step.title}
                  className="group relative rounded-3xl border border-gray-200 bg-white p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-orange-300 hover:shadow-xl hover:shadow-gray-200/70"
                >
                  <div className="relative z-10 flex h-16 w-16 items-center justify-center rounded-2xl border border-gray-200 bg-white shadow-sm transition duration-300 group-hover:rotate-3 group-hover:border-orange-300">
                    <Icon className="h-7 w-7 text-[#F0600E]" />
                  </div>

                  <div className="mt-7 font-['JetBrains_Mono'] text-xs font-semibold text-gray-400">
                    STEP {String(index + 1).padStart(2, "0")}
                  </div>

                  <h3 className="mt-3 text-xl font-bold text-gray-950">
                    {step.title}
                  </h3>

                  <p className="mt-3 text-sm leading-6 text-gray-600">
                    {step.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}