import { Activity, BarChart3, FileText, Flag, Home, Settings, Target, User, Users } from "lucide-react";
import { Link, NavLink, Outlet } from "react-router-dom";
import Logo from "../../../components/shared/Logo";
import { useAuth } from "../../auth/context/AuthContext";
import { ROUTES } from "../../../constants/routes";
import UserMenu from "../../../components/layout/UserMenu";
const navItems = [
  { label: "Home", href: "/console/athlete", icon: Home },
  { label: "Performances", href: "/console/athlete/performances", icon: Activity },
  { label: "Coaches", href: "/console/athlete/coaches", icon: Users },
  { label: "Progress", href: "/console/athlete/progress", icon: BarChart3 },
  { label: "Goals", href: "/console/athlete/goals", icon: Flag },
  { label: "Reports", href: "/console/athlete/reports", icon: FileText },
  { label: "Discover", href: "/console/athlete/discover", icon: Target },
  { label: "Profile", href: "/console/athlete/profile", icon: User },
  { label: "Settings", href: "/console/athlete/settings", icon: Settings },
];

export default function AthleteLayout() {
  const { user, signOut } = useAuth();

  return (
    <div className="min-h-screen bg-[#FAFAF7]">
      <aside className="fixed left-0 top-0 hidden h-screen w-72 border-r border-gray-200 bg-white px-5 py-6 lg:block">
        <Link to={ROUTES.ATHLETE.HOME}>
  <Logo />
</Link>

        <nav className="mt-10 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;

            return (
             <NavLink
  key={item.label}
  to={item.href}
  end={item.href === "/console/athlete"}
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

        <button
          onClick={signOut}
          className="absolute bottom-6 left-5 right-5 cursor-pointer rounded-2xl border border-gray-200 px-4 py-3 text-sm font-bold text-gray-700 transition hover:border-[#F0600E] hover:text-[#F0600E]"
        >
          Sign out
        </button>
      </aside>

      <main className="lg:pl-72">
        <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/85 px-6 py-4 backdrop-blur-xl lg:px-10">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-gray-400">
                Performance Centre
              </p>
              <p className="mt-1 text-sm font-semibold text-gray-700">
                {user?.email}
              </p>
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