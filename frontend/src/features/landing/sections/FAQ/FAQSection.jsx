import { motion } from "framer-motion";

import { Container, Section } from "@/shared/components";
import { fadeUp, staggerContainer } from "@/shared/animations";

import { faqContent } from "./faq.content";

export default function FAQSection() {
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
            {faqContent.eyebrow}
          </motion.p>

          <motion.h2
            variants={fadeUp}
            className="mt-6 text-5xl font-black leading-tight text-white"
          >
            {faqContent.title}
          </motion.h2>
        </motion.div>

        <div className="mx-auto mt-16 grid max-w-4xl gap-5">
          {faqContent.faqs.map((faq, index) => (
            <motion.div
              key={faq.question}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08, duration: 0.5 }}
              className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
            >
              <h3 className="text-xl font-bold text-white">
                {faq.question}
              </h3>

              <p className="mt-3 leading-7 text-slate-400">
                {faq.answer}
              </p>
            </motion.div>
          ))}
        </div>
      </Container>
    </Section>
  );
}