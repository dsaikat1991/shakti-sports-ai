import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../features/auth/context/AuthContext";
import { roleHomeRoute } from "../../constants/routes";
import type { UserRole } from "../../features/auth/types/auth";

// Sits inside ProtectedRoute (auth already confirmed). Blocks a
// signed-in user with the wrong role from reaching a console that isn't
// theirs - e.g. a coach directly navigating to /console/athlete, which
// would otherwise render (RLS just returns empty data, but the UI would
// look broken/confusing rather than redirecting somewhere sensible).
//
// role === null means the user is authenticated but hasn't finished
// onboarding yet (no profiles row exists). That's a normal transient
// state, not a violation - let it through rather than bouncing someone
// who hasn't picked a role yet.
export default function RoleGate({ allow }: { allow: UserRole[] }) {
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

  if (role !== null && !allow.includes(role)) {
    return <Navigate to={roleHomeRoute(role)} replace />;
  }

  return <Outlet />;
}
