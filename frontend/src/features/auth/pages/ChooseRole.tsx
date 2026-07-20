import { Building2, Dumbbell, Target } from "lucide-react";
import { useNavigate } from "react-router-dom";
import RoleCard from "../components/RoleCard";

export default function ChooseRole() {
  const navigate = useNavigate();

  return (
    <div className="w-full">
      <div className="mx-auto max-w-3xl text-center">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-brand-action">
          Choose your journey
        </p>

        <h1 className="mt-4 text-2xl font-bold text-text-primary md:text-3xl">
          Who are you?
        </h1>

        <p className="mx-auto mt-4 max-w-xl text-base leading-7 text-text-secondary">
          This helps Shakti create the right experience for your performance
          journey.
        </p>
      </div>

      <div className="mx-auto mt-12 grid max-w-6xl gap-5 lg:grid-cols-3">
        <RoleCard
          icon={Dumbbell}
          title="Athlete"
          description="Upload performances, receive AI reports, and track progress."
          points={["Upload videos", "Build profile", "Get discovered"]}
          accent="orange"
          onClick={() => navigate("/onboarding/athlete")}
        />

        <RoleCard
          icon={Target}
          title="Coach"
          description="Discover athletes, review reports, and create shortlists."
          points={["Search athletes", "Compare reports", "Invite talent"]}
          accent="green"
          onClick={() => navigate("/onboarding/coach")}
        />

        <RoleCard
          icon={Building2}
          title="Academy"
          description="Manage athletes, monitor progress, and support coaches."
          points={["Manage squads", "Track progress", "Organize reports"]}
          accent="blue"
          onClick={() => navigate("/onboarding/academy")}
        />
      </div>
    </div>
  );
}