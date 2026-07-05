import { motion } from "framer-motion";
import { ShieldCheck, Target, Zap } from "lucide-react";

const floatingCards = [
  {
    label: "Scout Match",
    value: "89%",
    icon: Target,
    className: "-left-8 top-24",
    color: "text-cyan-400",
  },
  {
    label: "AI Verified",
    value: "Video",
    icon: ShieldCheck,
    className: "-right-8 top-40",
    color: "text-green-400",
  },
  {
    label: "Speed",
    value: "+8%",
    icon: Zap,
    className: "-left-6 bottom-28",
    color: "text-yellow-400",
  },
];

export default function HeroFloatingCards() {
  return (
    <>
      {floatingCards.map((card, index) => {
        const Icon = card.icon;

        return (
          <motion.div
            key={card.label}
            animate={{ y: [-8, 8, -8] }}
            transition={{
              duration: 5 + index,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className={`absolute z-30 hidden min-w-37.5 rounded-2xl border border-white/10 bg-[#0B1224]/95 px-4 py-3 shadow-[0_0_40px_rgba(34,211,238,0.12)] backdrop-blur-xl xl:block ${card.className}`}
          >
            <div className="flex items-center gap-3">
              <Icon className={`h-5 w-5 shrink-0 ${card.color}`} />

              <div>
                <p className="text-xs text-slate-400">{card.label}</p>
                <p className="font-bold text-white">{card.value}</p>
              </div>
            </div>
          </motion.div>
        );
      })}
    </>
  );
}