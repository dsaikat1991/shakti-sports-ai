import { motion } from "framer-motion";
import { Search, BrainCircuit, Trophy } from "lucide-react";

import {
  Container,
  Section,
} from "@/shared/components";

import { fadeUp, staggerContainer } from "@/shared/animations";
import { missionContent } from "./mission.content";

const icons = [
  Search,
  BrainCircuit,
  Trophy,
];

export default function MissionSection() {
  return (
    <Section className="py-28">
      <Container>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid items-center gap-20 lg:grid-cols-2"
        >

          {/* Left */}

          <div>

            <motion.p
              variants={fadeUp}
              className="text-sm font-semibold tracking-[0.3em] text-cyan-400 uppercase"
            >
              {missionContent.eyebrow}
            </motion.p>

            <motion.h2
              variants={fadeUp}
              className="mt-6 text-5xl font-black text-white"
            >
              {missionContent.title}
            </motion.h2>

            <motion.p
              variants={fadeUp}
              className="mt-8 text-lg leading-8 text-slate-400"
            >
              {missionContent.description}
            </motion.p>

          </div>

          {/* Right */}

          <div className="space-y-8">

            {missionContent.points.map((item, index) => {

              const Icon = icons[index];

              return (

                <motion.div
                  key={item.title}
                  variants={fadeUp}
                  className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl"
                >

                  <Icon className="mb-5 h-10 w-10 text-cyan-400" />

                  <h3 className="text-2xl font-bold text-white">
                    {item.title}
                  </h3>

                  <p className="mt-3 leading-7 text-slate-400">
                    {item.description}
                  </p>

                </motion.div>

              );

            })}

          </div>

        </motion.div>

      </Container>
    </Section>
  );
}