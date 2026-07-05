import { motion } from "framer-motion";

import { Container, Section } from "@/shared/components";

import { testimonialsContent } from "./testimonials.content";

export default function TestimonialsSection() {
  return (
    <Section className="bg-[#070B18]">
      <Container>
        <div className="mx-auto max-w-4xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">
            {testimonialsContent.eyebrow}
          </p>

          <h2 className="mt-6 text-5xl font-black leading-tight text-white">
            {testimonialsContent.title}
          </h2>
        </div>

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {testimonialsContent.testimonials.map((item, index) => (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08, duration: 0.5 }}
              className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl"
            >
              <p className="text-lg leading-8 text-slate-300">
                “{item.quote}”
              </p>

              <div className="mt-8">
                <p className="font-bold text-white">{item.name}</p>
                <p className="mt-1 text-sm text-slate-500">{item.role}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </Container>
    </Section>
  );
}