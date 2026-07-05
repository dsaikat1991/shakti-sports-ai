import { motion } from "framer-motion";

import HeroFloatingCards from "./HeroFloatingCards";
import AIScoreCircle from "./components/AIScoreCircle";
import MetricBar from "./components/MetricBar";
import { heroAthlete } from "./hero.mock";

export default function HeroVisual() {
  return (
    <motion.div
      initial={{ opacity: 0, x: 60 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.8 }}
      className="relative min-h-140"
    >
      {/* Floating Cards */}

      <HeroFloatingCards />

      {/* Dashboard */}

      <div
        className="
          absolute
          left-1/2
          top-1/2
          w-full
          max-w-lg
          -translate-x-1/2
          -translate-y-1/2
          rounded-3xl
          border
          border-white/10
          bg-white/5
          p-8
          shadow-[0_0_80px_rgba(34,211,238,0.15)]
          backdrop-blur-xl
        "
      >
        {/* Header */}

        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-cyan-400">
              AI Performance Report
            </p>

            <h3 className="mt-3 text-3xl font-black text-white">
              {heroAthlete.name}
            </h3>

            <p className="mt-1 text-slate-400">
              {heroAthlete.event}
            </p>
          </div>

          <AIScoreCircle score={heroAthlete.score} />
        </div>

        <div className="my-8 h-px bg-white/10" />

        {/* Metrics */}

        <div className="space-y-6">
          {heroAthlete.metrics.map((metric) => (
            <MetricBar
              key={metric.label}
              label={metric.label}
              value={metric.value}
            />
          ))}
        </div>

        {/* Verdict */}

        <div className="mt-10 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-5">
          <p className="text-sm text-cyan-300">
            AI Verdict
          </p>

          <p className="mt-2 text-lg font-semibold text-white">
            {heroAthlete.verdict}
          </p>
        </div>
      </div>
    </motion.div>
  );
}