import { motion } from "framer-motion";

import { Container, Section } from "@/shared/components";
import { fadeUp, staggerContainer } from "@/shared/animations";

import { journeyContent } from "./journey.content";

export default function JourneySection() {
  return (
    <Section className="bg-[#070B18]">
      <Container>
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="mx-auto max-w-4xl text-center"
        >
          <motion.p
            variants={fadeUp}
            className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400"
          >
            {journeyContent.eyebrow}
          </motion.p>

          <motion.h2
            variants={fadeUp}
            className="mt-6 text-5xl font-black leading-tight text-white"
          >
            {journeyContent.title}
          </motion.h2>

          <motion.p
            variants={fadeUp}
            className="mt-8 text-lg leading-8 text-slate-400"
          >
            {journeyContent.description}
          </motion.p>
        </motion.div>

        <div className="relative mt-20">
          <div className="absolute left-0 top-10 hidden h-px w-full bg-linear-to-r from-transparent via-cyan-400/40 to-transparent lg:block" />

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-6">
            {journeyContent.steps.map((step, index) => {
              const Icon = step.icon;

              return (
                <motion.div
                  key={step.title}
                  initial={{ opacity: 0, y: 32 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.08, duration: 0.5 }}
                  className="relative rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
                >
                  <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-400">
                    <Icon className="h-7 w-7" />
                  </div>

                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
                    Step {index + 1}
                  </p>

                  <h3 className="mt-3 text-xl font-bold text-white">
                    {step.title}
                  </h3>

                  <p className="mt-4 text-sm leading-6 text-slate-400">
                    {step.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </Container>
    </Section>
  );
}