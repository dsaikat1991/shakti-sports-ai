import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import Hero from "./features/home/components/Hero";
import PerformanceSummary from "./features/home/components/PerformanceSummary";
import AIPerformanceAnalysis from "./features/home/components/AIPerformanceAnalysis";
import HowItWorks from "./features/home/components/HowItWorks";
import AthleteJourney from "./features/home/components/AthleteJourney";
import CoachTalentSection from "./features/home/components/CoachTalentSection";
import OlympicEvents from "./features/home/components/OlympicEvents";
import FinalCTA from "./features/home/components/FinalCTA";

function App() {
  return (
    <>
      <Navbar />
      <Hero />
      <PerformanceSummary />
      <AIPerformanceAnalysis />
      <HowItWorks />
      <AthleteJourney />
      <CoachTalentSection />
      <OlympicEvents />
      <FinalCTA />
      <Footer />
    </>
  );
}

export default App;