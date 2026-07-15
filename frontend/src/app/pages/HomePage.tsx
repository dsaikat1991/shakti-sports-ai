import { Navigate } from "react-router-dom";

import { useAuth } from "../../features/auth/context/AuthContext";
import { roleHomeRoute } from "../../constants/routes";

import Hero from "../../features/home/components/Hero";
import PerformanceSummary from "../../features/home/components/PerformanceSummary";
import AIPerformanceAnalysis from "../../features/home/components/AIPerformanceAnalysis";
import HowItWorks from "../../features/home/components/HowItWorks";
import AthleteJourney from "../../features/home/components/AthleteJourney";
import CoachTalentSection from "../../features/home/components/CoachTalentSection";
import OlympicEvents from "../../features/home/components/OlympicEvents";
import FinalCTA from "../../features/home/components/FinalCTA";

export default function HomePage() {
  const { user, role, roleLoading } = useAuth();

  if (user && roleLoading) {
    // Avoid a flash of marketing content before we know where a signed-in
    // user actually belongs (athlete/coach/academy console are different
    // destinations - see roleHomeRoute).
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
          Loading Shakti...
        </p>
      </div>
    );
  }

  if (user) {
    return <Navigate to={roleHomeRoute(role)} replace />;
  }

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