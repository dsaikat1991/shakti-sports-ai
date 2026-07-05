import { motion } from "framer-motion";

import { Container, Section } from "@/shared/components";
import { fadeUp, staggerContainer } from "@/shared/animations";

import { howItWorksContent } from "./howItWorks.content";

export default function HowItWorksSection() {
  return (
    <Section id="how-it-works">
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
            {howItWorksContent.eyebrow}
          </motion.p>

          <motion.h2
            variants={fadeUp}
            className="mt-6 text-5xl font-black leading-tight text-white"
          >
            {howItWorksContent.title}
          </motion.h2>

          <motion.p
            variants={fadeUp}
            className="mt-8 text-lg leading-8 text-slate-400"
          >
            {howItWorksContent.description}
          </motion.p>
        </motion.div>

        <div className="mt-20 grid gap-8 lg:grid-cols-3">
          {howItWorksContent.steps.map((step, index) => {
            const Icon = step.icon;

            return (
              <motion.div
                key={step.title}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="relative rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl"
              >
                <div className="mb-8 flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-400">
                  <Icon className="h-7 w-7" />
                </div>

                <p className="text-sm font-semibold text-cyan-400">
                  Step {index + 1}
                </p>

                <h3 className="mt-3 text-2xl font-bold text-white">
                  {step.title}
                </h3>

                <p className="mt-4 leading-7 text-slate-400">
                  {step.description}
                </p>
              </motion.div>
            );
          })}
        </div>
      </Container>
    </Section>
  );
}