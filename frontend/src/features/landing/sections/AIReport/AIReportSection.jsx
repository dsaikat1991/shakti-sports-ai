import { motion } from "framer-motion";

import { Container, Section } from "@/shared/components";
import { fadeUp, staggerContainer } from "@/shared/animations";

import { aiReportContent } from "./aiReport.content";

export default function AIReportSection() {
  return (
    <Section className="bg-[#070B18]">
      <Container>
        <div className="grid items-center gap-16 lg:grid-cols-2">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <motion.p
              variants={fadeUp}
              className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400"
            >
              {aiReportContent.eyebrow}
            </motion.p>

            <motion.h2
              variants={fadeUp}
              className="mt-6 text-5xl font-black leading-tight text-white"
            >
              {aiReportContent.title}
            </motion.h2>

            <motion.p
              variants={fadeUp}
              className="mt-8 text-lg leading-8 text-slate-400"
            >
              {aiReportContent.description}
            </motion.p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 48 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-[0_0_80px_rgba(34,211,238,0.12)] backdrop-blur-xl"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-cyan-400">
                  Sample Report
                </p>

                <h3 className="mt-3 text-3xl font-black text-white">
                  AI Score 92
                </h3>
              </div>

              <div className="rounded-full border border-cyan-400/40 bg-cyan-500/10 px-5 py-3 font-bold text-cyan-300">
                Ready
              </div>
            </div>

            <div className="mt-10 space-y-6">
              {aiReportContent.metrics.map((metric) => (
                <div key={metric.label}>
                  <div className="mb-2 flex justify-between text-sm">
                    <span className="text-slate-400">{metric.label}</span>
                    <span className="font-semibold text-white">
                      {metric.value}
                    </span>
                  </div>

                  <div className="h-2 overflow-hidden rounded-full bg-white/10">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: `${metric.value}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 1 }}
                      className="h-full rounded-full bg-cyan-400"
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-10 rounded-2xl border border-white/10 bg-[#0B1224] p-5">
              <p className="mb-4 font-semibold text-white">AI Observations</p>

              <ul className="space-y-3 text-sm text-slate-400">
                {aiReportContent.insights.map((item) => (
                  <li key={item}>✓ {item}</li>
                ))}
              </ul>
            </div>
          </motion.div>
        </div>
      </Container>
    </Section>
  );
}