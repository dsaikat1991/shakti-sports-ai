import { Link } from "react-router-dom";
import { Compass } from "lucide-react";
import { ROUTES } from "../../constants/routes";
import { useAuth } from "../../features/auth/context/AuthContext";

export default function NotFound() {
  const { user } = useAuth();

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-2xl flex-col items-center justify-center px-6 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-action-soft text-brand-action">
        <Compass className="h-7 w-7" />
      </div>

      <p className="mt-5 font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-brand-action">
        404
      </p>

      <h1 className="mt-4 text-2xl font-bold text-text-primary md:text-3xl">
        Page Not Found
      </h1>

      <p className="mx-auto mt-4 max-w-md text-base leading-7 text-text-secondary">
        The page you're looking for doesn't exist or may have moved.
      </p>

      <Link
        to={user ? ROUTES.ATHLETE.HOME : ROUTES.HOME}
        className="mt-8 inline-flex rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover"
      >
        {user ? "Back to Dashboard" : "Back to Home"}
      </Link>
    </div>
  );
}
