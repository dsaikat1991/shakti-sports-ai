import { ArrowRight, Play } from "lucide-react";

import { Badge, Button } from "@/shared/components";

export default function HeroContent() {
  return (
    <div className="relative z-10 max-w-xl">
      <Badge>India's AI Talent Discovery Platform</Badge>

      <h1 className="mt-8 text-5xl font-black leading-tight text-white md:text-7xl">
        Every Champion
        <span className="block text-cyan-400">Deserves To</span>
        <span className="block">Be Discovered.</span>
      </h1>

      <p className="mt-8 text-xl leading-8 text-slate-400">
        Upload one performance video. Receive AI-assisted insights. Get
        discovered by coaches, academies and scouts.
      </p>

      <div className="mt-10 flex flex-wrap gap-4">
        <Button size="lg">
          Get AI Analysis <ArrowRight className="h-5 w-5" />
        </Button>

        <Button variant="secondary" size="lg">
          <Play className="h-5 w-5" /> Watch Demo
        </Button>
      </div>
    </div>
  );
}