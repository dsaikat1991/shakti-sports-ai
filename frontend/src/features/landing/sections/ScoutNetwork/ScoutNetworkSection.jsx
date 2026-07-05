import { motion } from "framer-motion";

import { Container, Section } from "@/shared/components";
import { fadeUp, staggerContainer } from "@/shared/animations";

import { scoutNetworkContent } from "./scoutNetwork.content";

export default function ScoutNetworkSection() {
  return (
    <Section>
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
              {scoutNetworkContent.eyebrow}
            </motion.p>

            <motion.h2
              variants={fadeUp}
              className="mt-6 text-5xl font-black leading-tight text-white"
            >
              {scoutNetworkContent.title}
            </motion.h2>

            <motion.p
              variants={fadeUp}
              className="mt-8 text-lg leading-8 text-slate-400"
            >
              {scoutNetworkContent.description}
            </motion.p>
          </motion.div>

          <div className="grid gap-6 sm:grid-cols-2">
            {scoutNetworkContent.features.map((feature, index) => {
              const Icon = feature.icon;

              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 28 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.08, duration: 0.5 }}
                  className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
                >
                  <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-400">
                    <Icon className="h-6 w-6" />
                  </div>

                  <h3 className="text-xl font-bold text-white">
                    {feature.title}
                  </h3>

                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    {feature.description}
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