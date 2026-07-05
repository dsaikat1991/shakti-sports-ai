import { motion } from "framer-motion";
import { ArrowRight, Play } from "lucide-react";

import { fadeUp, staggerContainer } from "@/shared/animations";
import { Badge, Button } from "@/shared/components";

export default function HeroContent() {
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      className="relative z-10 max-w-xl"
    >
      {/* Badge */}

      <motion.div variants={fadeUp}>
        <Badge>🇮🇳 India's AI Talent Discovery Platform</Badge>
      </motion.div>

      {/* Heading */}

      <motion.h1
        variants={fadeUp}
        className="mt-8 text-5xl font-black leading-tight text-white md:text-7xl"
      >
        Every Champion

        <span className="block text-cyan-400">
          Deserves To
        </span>

        <span className="block">
          Be Discovered.
        </span>
      </motion.h1>

      {/* Description */}

      <motion.p
        variants={fadeUp}
        className="mt-8 text-xl leading-8 text-slate-400"
      >
        Upload one sports performance video.

        Receive AI-powered athlete insights.

        Get discovered by coaches, academies and scouts across India.
      </motion.p>

      {/* CTA Buttons */}

      <motion.div
        variants={fadeUp}
        className="mt-10 flex flex-wrap gap-4"
      >
        <Button size="lg">
          Get AI Analysis

          <ArrowRight className="h-5 w-5" />
        </Button>

        <Button
          variant="secondary"
          size="lg"
        >
          <Play className="h-5 w-5" />

          Watch Demo
        </Button>
      </motion.div>

      {/* Trust Indicators */}

      <motion.div
        variants={fadeUp}
        className="mt-10 flex flex-wrap gap-6 text-sm text-slate-400"
      >
        <div className="flex items-center gap-2">
          <span className="text-cyan-400">✓</span>

          AI Performance Analysis
        </div>

        <div className="flex items-center gap-2">
          <span className="text-cyan-400">✓</span>

          Built for Indian Athletes
        </div>

        <div className="flex items-center gap-2">
          <span className="text-cyan-400">✓</span>

          Coach & Scout Ready
        </div>
      </motion.div>
    </motion.div>
  );
}