import { Activity, TrendingUp, FileText, Flag, Home, Menu, Settings, Target, User, Users, X } from "lucide-react";
import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import Logo from "../../../components/shared/Logo";
import { useAuth } from "../../auth/context/AuthContext";
import { ROUTES } from "../../../constants/routes";
import UserMenu from "../../../components/layout/UserMenu";
const navItems = [
  { label: "Home", href: ROUTES.ATHLETE.HOME, icon: Home },
  { label: "Performances", href: ROUTES.ATHLETE.HISTORY, icon: Activity },
  { label: "Coaches", href: ROUTES.ATHLETE.COACHES, icon: Users },
  { label: "My Progress", href: ROUTES.ATHLETE.TWIN, icon: TrendingUp },
  { label: "Goals", href: ROUTES.ATHLETE.GOALS, icon: Flag },
  { label: "Reports", href: ROUTES.ATHLETE.REPORTS, icon: FileText },
  { label: "Discover", href: ROUTES.ATHLETE.DISCOVER, icon: Target },
  { label: "Profile", href: ROUTES.ATHLETE.PROFILE, icon: User },
  { label: "Settings", href: ROUTES.ATHLETE.SETTINGS, icon: Settings },
];

function AthleteNavLinks({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="mt-8 space-y-0.5">
      {navItems.map((item) => {
        const Icon = item.icon;

        return (
          <NavLink
            key={item.label}
            to={item.href}
            end={item.href === ROUTES.ATHLETE.HOME}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                isActive
                  ? "bg-brand-action-soft text-brand-action-ink"
                  : "text-text-secondary hover:bg-surface-sunken hover:text-text-primary"
              }`
            }
          >
            <Icon className="h-4.5 w-4.5" />
            {item.label}
          </NavLink>
        );
      })}
    </nav>
  );
}

export default function AthleteLayout() {
  const { user, signOut } = useAuth();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface-canvas">
      <aside className="fixed left-0 top-0 hidden h-screen w-64 border-r border-border-default bg-surface-card px-4 py-6 lg:block">
        <Link to={ROUTES.ATHLETE.HOME} className="px-1">
          <Logo />
        </Link>

        <AthleteNavLinks />

        <button
          onClick={signOut}
          className="absolute bottom-6 left-4 right-4 cursor-pointer rounded-xl border border-border-default px-4 py-2.5 text-sm font-semibold text-text-secondary transition hover:border-text-disabled hover:text-text-primary"
        >
          Sign out
        </button>
      </aside>

      {mobileNavOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            aria-label="Close menu"
            onClick={() => setMobileNavOpen(false)}
            className="absolute inset-0 cursor-default bg-gray-950/40 backdrop-blur-sm"
          />

          <aside className="relative flex h-full w-64 max-w-[80vw] flex-col overflow-y-auto border-r border-border-default bg-surface-card px-4 py-6 shadow-2xl">
            <div className="flex items-center justify-between px-1">
              <Link to={ROUTES.ATHLETE.HOME} onClick={() => setMobileNavOpen(false)}>
                <Logo />
              </Link>

              <button
                type="button"
                aria-label="Close menu"
                onClick={() => setMobileNavOpen(false)}
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-border-default text-text-muted hover:border-text-disabled hover:text-text-primary"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <AthleteNavLinks onNavigate={() => setMobileNavOpen(false)} />

            <button
              onClick={signOut}
              className="mt-6 cursor-pointer rounded-xl border border-border-default px-4 py-2.5 text-sm font-semibold text-text-secondary transition hover:border-text-disabled hover:text-text-primary"
            >
              Sign out
            </button>
          </aside>
        </div>
      )}

      <main className="lg:pl-64">
        <header className="sticky top-0 z-40 border-b border-border-default bg-surface-card/85 px-6 py-4 backdrop-blur-xl lg:px-10">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                type="button"
                aria-label="Open menu"
                onClick={() => setMobileNavOpen(true)}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-border-default text-text-secondary hover:border-text-disabled hover:text-text-primary lg:hidden"
              >
                <Menu className="h-5 w-5" />
              </button>

              <div>
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.08em] text-text-muted">
                  Performance Centre
                </p>
                <p className="mt-1 truncate text-sm font-semibold text-text-secondary">
                  {user?.email}
                </p>
              </div>
            </div>

            <UserMenu />
          </div>
        </header>

        <div className="px-6 py-8 lg:px-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
