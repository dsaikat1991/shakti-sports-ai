import { Activity, Fingerprint, FileText, Flag, Home, Menu, Settings, Target, User, Users, X } from "lucide-react";
import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import Logo from "../../../components/shared/Logo";
import { useAuth } from "../../auth/context/AuthContext";
import { ROUTES } from "../../../constants/routes";
import UserMenu from "../../../components/layout/UserMenu";
const navItems = [
  { label: "Home", href: "/console/athlete", icon: Home },
  { label: "Performances", href: "/console/athlete/performances", icon: Activity },
  { label: "Coaches", href: "/console/athlete/coaches", icon: Users },
  { label: "Digital Twin", href: "/console/athlete/twin", icon: Fingerprint },
  { label: "Goals", href: "/console/athlete/goals", icon: Flag },
  { label: "Reports", href: "/console/athlete/reports", icon: FileText },
  { label: "Discover", href: "/console/athlete/discover", icon: Target },
  { label: "Profile", href: "/console/athlete/profile", icon: User },
  { label: "Settings", href: "/console/athlete/settings", icon: Settings },
];

function AthleteNavLinks({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="mt-10 space-y-2">
      {navItems.map((item) => {
        const Icon = item.icon;

        return (
          <NavLink
            key={item.label}
            to={item.href}
            end={item.href === "/console/athlete"}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                isActive
                  ? "bg-orange-50 text-[#F0600E]"
                  : "text-gray-600 hover:bg-orange-50 hover:text-[#F0600E]"
              }`
            }
          >
            <Icon className="h-5 w-5" />
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
    <div className="min-h-screen bg-[#FAFAF7]">
      <aside className="fixed left-0 top-0 hidden h-screen w-72 border-r border-gray-200 bg-white px-5 py-6 lg:block">
        <Link to={ROUTES.ATHLETE.HOME}>
          <Logo />
        </Link>

        <AthleteNavLinks />

        <button
          onClick={signOut}
          className="absolute bottom-6 left-5 right-5 cursor-pointer rounded-2xl border border-gray-200 px-4 py-3 text-sm font-bold text-gray-700 transition hover:border-[#F0600E] hover:text-[#F0600E]"
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

          <aside className="relative flex h-full w-72 max-w-[80vw] flex-col overflow-y-auto border-r border-gray-200 bg-white px-5 py-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <Link to={ROUTES.ATHLETE.HOME} onClick={() => setMobileNavOpen(false)}>
                <Logo />
              </Link>

              <button
                type="button"
                aria-label="Close menu"
                onClick={() => setMobileNavOpen(false)}
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-gray-200 text-gray-500 hover:border-[#F0600E] hover:text-[#F0600E]"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <AthleteNavLinks onNavigate={() => setMobileNavOpen(false)} />

            <button
              onClick={signOut}
              className="mt-6 cursor-pointer rounded-2xl border border-gray-200 px-4 py-3 text-sm font-bold text-gray-700 transition hover:border-[#F0600E] hover:text-[#F0600E]"
            >
              Sign out
            </button>
          </aside>
        </div>
      )}

      <main className="lg:pl-72">
        <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/85 px-6 py-4 backdrop-blur-xl lg:px-10">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                type="button"
                aria-label="Open menu"
                onClick={() => setMobileNavOpen(true)}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-gray-200 text-gray-600 hover:border-[#F0600E] hover:text-[#F0600E] lg:hidden"
              >
                <Menu className="h-5 w-5" />
              </button>

              <div>
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
                  Performance Centre
                </p>
                <p className="mt-1 truncate text-sm font-semibold text-gray-700">
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
