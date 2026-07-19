import {
  Bookmark,
  GitCompare,
  Home,
  Inbox,
  ListChecks,
  Menu,
  Search,
  Settings,
  User,
  Users,
  X,
} from "lucide-react";
import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import Logo from "../../../components/shared/Logo";
import { useAuth } from "../../auth/context/AuthContext";
import { ROUTES } from "../../../constants/routes";
import UserMenu from "../../../components/layout/UserMenu";

// Coach and academy consoles are structurally identical - one shell,
// role-driven copy - rather than two near-duplicate layout components.
export default function PartnerLayout() {
  const { user, role, signOut } = useAuth();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const isAcademy = role === "academy";
  const routeSet = isAcademy ? ROUTES.ACADEMY : ROUTES.COACH;

  const navItems = [
    { label: "Home", href: routeSet.HOME, icon: Home },
    { label: isAcademy ? "Squad" : "My Athletes", href: routeSet.ATHLETES, icon: Users },
    { label: "Requests", href: routeSet.REQUESTS, icon: Inbox },
    { label: "Discover", href: routeSet.DISCOVER, icon: Search },
    { label: "Bookmarks", href: routeSet.BOOKMARKS, icon: Bookmark },
    { label: "Lists", href: routeSet.LISTS, icon: ListChecks },
    { label: "Compare", href: routeSet.COMPARE, icon: GitCompare },
    { label: "Profile", href: routeSet.PROFILE, icon: User },
    { label: "Settings", href: routeSet.SETTINGS, icon: Settings },
  ];

  function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
    return (
      <nav className="mt-10 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.label}
              to={item.href}
              end={item.href === routeSet.HOME}
              onClick={onNavigate}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                  isActive
                    ? "bg-brand-action-soft text-brand-action"
                    : "text-text-secondary hover:bg-brand-action-soft hover:text-brand-action"
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

  return (
    <div className="min-h-screen bg-surface-canvas">
      <aside className="fixed left-0 top-0 hidden h-screen w-72 border-r border-border-default bg-surface-card px-5 py-6 lg:block">
        <Link to={routeSet.HOME}>
          <Logo />
        </Link>

        <NavLinks />

        <button
          onClick={signOut}
          className="absolute bottom-6 left-5 right-5 cursor-pointer rounded-2xl border border-border-default px-4 py-3 text-sm font-bold text-text-secondary transition hover:border-brand-action hover:text-brand-action"
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

          <aside className="relative flex h-full w-72 max-w-[80vw] flex-col overflow-y-auto border-r border-border-default bg-surface-card px-5 py-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <Link to={routeSet.HOME} onClick={() => setMobileNavOpen(false)}>
                <Logo />
              </Link>

              <button
                type="button"
                aria-label="Close menu"
                onClick={() => setMobileNavOpen(false)}
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-border-default text-text-muted hover:border-brand-action hover:text-brand-action"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <NavLinks onNavigate={() => setMobileNavOpen(false)} />

            <button
              onClick={signOut}
              className="mt-6 cursor-pointer rounded-2xl border border-border-default px-4 py-3 text-sm font-bold text-text-secondary transition hover:border-brand-action hover:text-brand-action"
            >
              Sign out
            </button>
          </aside>
        </div>
      )}

      <main className="lg:pl-72">
        <header className="sticky top-0 z-40 border-b border-border-default bg-surface-card/85 px-6 py-4 backdrop-blur-xl lg:px-10">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                type="button"
                aria-label="Open menu"
                onClick={() => setMobileNavOpen(true)}
                className="flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-xl border border-border-default text-text-secondary transition hover:border-brand-action hover:text-brand-action lg:hidden"
              >
                <Menu className="h-5 w-5" />
              </button>

              <div>
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-text-disabled">
                  {isAcademy ? "Academy Console" : "Coach Console"}
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
