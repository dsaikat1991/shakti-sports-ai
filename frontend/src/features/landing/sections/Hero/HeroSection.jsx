import { Container, Section } from "@/shared/components";

import HeroBackground from "./HeroBackground";
import HeroContent from "./HeroContent";
import HeroParticles from "./HeroParticles";
import HeroVisual from "./HeroVisual";

export default function HeroSection() {
  return (
    <Section className="overflow-hidden bg-[#050816]">
      <HeroBackground />
      <HeroParticles />

      <Container>
        <div className="grid items-center gap-16 lg:grid-cols-2">
          <HeroContent />
          <HeroVisual />
        </div>
      </Container>
    </Section>
  );
}