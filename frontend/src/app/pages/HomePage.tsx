import Hero from "../../features/home/components/Hero";
import PerformanceSummary from "../../features/home/components/PerformanceSummary";
import AIPerformanceAnalysis from "../../features/home/components/AIPerformanceAnalysis";
import HowItWorks from "../../features/home/components/HowItWorks";
import AthleteJourney from "../../features/home/components/AthleteJourney";
import CoachTalentSection from "../../features/home/components/CoachTalentSection";
import OlympicEvents from "../../features/home/components/OlympicEvents";
import FinalCTA from "../../features/home/components/FinalCTA";

export default function HomePage() {
  return (
    <>
      <Hero />
      <PerformanceSummary />
      <AIPerformanceAnalysis />
      <HowItWorks />
      <AthleteJourney />
      <CoachTalentSection />
      <OlympicEvents />
      <FinalCTA />
    </>
  );
}