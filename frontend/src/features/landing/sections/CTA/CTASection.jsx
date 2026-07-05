import { ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

import { Button, Container, Section } from "@/shared/components";
import { fadeUp, staggerContainer } from "@/shared/animations";

import { ctaContent } from "./cta.content";

export default function CTASection() {
  return (
    <Section className="bg-[#070B18]">
      <Container>
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-4xl border border-white/10 bg-white/5 px-8 py-20 text-center shadow-[0_0_100px_rgba(34,211,238,0.12)] backdrop-blur-xl"
        >
          <div className="absolute left-1/2 top-0 h-72 w-72 -translate-x-1/2 rounded-full bg-cyan-500/10 blur-[100px]" />

          <div className="relative z-10 mx-auto max-w-4xl">
            <motion.p
              variants={fadeUp}
              className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400"
            >
              {ctaContent.eyebrow}
            </motion.p>

            <motion.h2
              variants={fadeUp}
              className="mt-6 text-5xl font-black leading-tight text-white"
            >
              {ctaContent.title}
            </motion.h2>

            <motion.p
              variants={fadeUp}
              className="mx-auto mt-8 max-w-2xl text-lg leading-8 text-slate-400"
            >
              {ctaContent.description}
            </motion.p>

            <motion.div
              variants={fadeUp}
              className="mt-10 flex flex-wrap justify-center gap-4"
            >
              <Button size="lg">
                {ctaContent.primaryCta}
                <ArrowRight className="h-5 w-5" />
              </Button>

              <Button variant="secondary" size="lg">
                {ctaContent.secondaryCta}
              </Button>
            </motion.div>
          </div>
        </motion.div>
      </Container>
    </Section>
  );
}