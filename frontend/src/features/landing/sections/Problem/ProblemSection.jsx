import { motion } from "framer-motion";
import { MapPinOff, Activity, EyeOff, FileWarning } from "lucide-react";

import { Container, Section } from "@/shared/components";
import { fadeUp, staggerContainer } from "@/shared/animations";

import { problemContent } from "./problem.content";

const icons = [MapPinOff, Activity, EyeOff, FileWarning];

export default function ProblemSection() {
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
            {problemContent.eyebrow}
          </motion.p>

          <motion.h2
            variants={fadeUp}
            className="mt-6 text-5xl font-black leading-tight text-white"
          >
            {problemContent.title}
          </motion.h2>

          <motion.p
            variants={fadeUp}
            className="mt-8 text-lg leading-8 text-slate-400"
          >
            {problemContent.description}
          </motion.p>
        </motion.div>

        <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {problemContent.problems.map((item, index) => {
            const Icon = icons[index];

            return (
              <motion.div
                key={item}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
              >
                <Icon className="h-8 w-8 text-cyan-400" />

                <p className="mt-6 font-semibold leading-7 text-white">
                  {item}
                </p>
              </motion.div>
            );
          })}
        </div>
      </Container>
    </Section>
  );
}