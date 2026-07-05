import { motion } from "framer-motion";

export default function AIScoreCircle({ score }) {
  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      whileInView={{ scale: 1, opacity: 1 }}
      viewport={{ once: true }}
      className="flex h-24 w-24 items-center justify-center rounded-full border-4 border-cyan-400 bg-cyan-500/10 shadow-[0_0_40px_rgba(34,211,238,0.35)]"
    >
      <span className="text-3xl font-black text-white">{score}</span>
    </motion.div>
  );
}