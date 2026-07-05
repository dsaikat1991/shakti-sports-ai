import { AIReportSection } from "../sections/AIReport";
import { CTASection } from "../sections/CTA";
import { FAQSection } from "../sections/FAQ";
import { HeroSection } from "../sections/Hero";
import { HowItWorksSection } from "../sections/HowItWorks";
import { IndiaMapSection } from "../sections/IndiaMap";
import { JourneySection } from "../sections/Journey";
import { MissionSection } from "../sections/Mission";
import { ProblemSection } from "../sections/Problem";
import { ScoutNetworkSection } from "../sections/ScoutNetwork";
import { TestimonialsSection } from "../sections/Testimonials";

export default function LandingPage() {
  return (
    <>
      <HeroSection />
      <MissionSection />
      <ProblemSection />
      <HowItWorksSection />
      <AIReportSection />
      <IndiaMapSection />
      <JourneySection />
      <ScoutNetworkSection />
      <TestimonialsSection />
      <FAQSection />
      <CTASection />
    </>
  );
}