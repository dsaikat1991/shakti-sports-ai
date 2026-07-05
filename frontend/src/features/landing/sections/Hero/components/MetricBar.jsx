import { motion } from "framer-motion";

export default function MetricBar({ label, value }) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-sm">
        <span className="text-slate-400">{label}</span>
        <span className="font-semibold text-white">{value}</span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${value}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1 }}
          className="h-full rounded-full bg-cyan-400"
        />
      </div>
    </div>
  );
}