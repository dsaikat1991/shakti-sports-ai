import { motion } from "framer-motion";

import indiaMap from "@/assets/maps/india.svg";
import { Container, Section } from "@/shared/components";
import { fadeUp, staggerContainer } from "@/shared/animations";

import { indiaMapContent } from "./indiaMap.content";

export default function IndiaMapSection() {
  return (
    <Section>
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
            {indiaMapContent.eyebrow}
          </motion.p>

          <motion.h2
            variants={fadeUp}
            className="mt-6 text-5xl font-black leading-tight text-white"
          >
            {indiaMapContent.title}
          </motion.h2>

          <motion.p
            variants={fadeUp}
            className="mt-8 text-lg leading-8 text-slate-400"
          >
            {indiaMapContent.description}
          </motion.p>
        </motion.div>

        <div className="relative mx-auto mt-20 h-135 max-w-3xl">
          <div className="absolute inset-0 rounded-full bg-cyan-500/10 blur-[140px]" />

          <img
            src={indiaMap}
            alt="India talent map"
            className="absolute left-1/2 top-1/2 z-10 w-full max-w-md -translate-x-1/2 -translate-y-1/2 opacity-75"
          />

          <div className="absolute inset-0 z-20 -translate-x-8">
            {indiaMapContent.locations.map((location, index) => (
              <motion.div
                key={location.name}
                initial={{ scale: 0, opacity: 0 }}
                whileInView={{ scale: 1, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.15, duration: 0.4 }}
                className={`absolute ${location.position}`}
              >
                <span className="relative flex h-4 w-4">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400/70" />
                  <span className="absolute inset-0 rounded-full bg-cyan-400 opacity-70 blur-md" />
                  <span className="relative h-4 w-4 rounded-full bg-cyan-300 shadow-[0_0_25px_rgba(34,211,238,0.95)]" />
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </Container>
    </Section>
  );
}