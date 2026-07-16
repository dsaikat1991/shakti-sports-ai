import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../features/auth/context/AuthContext";
import { roleHomeRoute } from "../../constants/routes";

// Sits around /choose-role and /onboarding/* - blocks a user who has
// ALREADY finished onboarding (a profiles row with a role already
// exists) from re-entering role selection/onboarding. Without this,
// onboarding's own "Finish" step re-inserts a profiles row keyed by the
// same user id and crashes on a profiles_pkey duplicate-key violation.
// Most commonly hit via Google OAuth: signInWithGoogle()'s redirectTo is
// hardcoded to /choose-role regardless of whether the signing-in user
// is new or returning, unlike the email/password path, which checks
// getUserRole() and routes via roleHomeRoute() itself.
//
// role === null (no profiles row yet, still picking a role) is let
// through - that's the normal, intended use of these routes.
export default function RequireNoRole() {
  const { role, roleLoading } = useAuth();

  if (roleLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
          Loading Shakti...
        </p>
      </div>
    );
  }

  if (role !== null) {
    return <Navigate to={roleHomeRoute(role)} replace />;
  }

  return <Outlet />;
}
