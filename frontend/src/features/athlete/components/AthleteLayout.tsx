import { Activity, Bell, TrendingUp, FileText, Flag, Home, Menu, Settings, Target, Upload, User, Users, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import IconButton from "../../../components/ui/IconButton";
import Logo from "../../../components/shared/Logo";
import { useAuth } from "../../auth/context/AuthContext";
import { ROUTES } from "../../../constants/routes";
import UserMenu from "../../../components/layout/UserMenu";
import { useAthleteNotifications } from "../hooks/useAthleteNotifications";
import { notificationIcon } from "../lib/deriveNotifications";
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

function NotificationsMenu({
  notifications,
}: {
  notifications: ReturnType<typeof useAthleteNotifications>["notifications"];
}) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const hasNotifications = notifications.length > 0;

  useEffect(() => {
    if (!open) return;

    function handlePointerDown(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  return (
    <div className="relative" ref={containerRef}>
      <IconButton
        icon={Bell}
        label="Notifications"
        ariaExpanded={open}
        hasIndicator={hasNotifications}
        onClick={() => setOpen((current) => !current)}
      />

      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-2xl border border-border-default bg-surface-card p-2 shadow-xl">
          <p className="px-3 py-2 font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.15em] text-text-muted">
            Notifications
          </p>

          {notifications.length === 0 ? (
            <p className="px-3 py-4 text-sm leading-6 text-text-muted">
              You're all caught up - nothing new to review.
            </p>
          ) : (
            <div className="flex flex-col">
              {notifications.slice(0, 5).map((notification) => {
                const Icon = notificationIcon(notification.type);

                return (
                  <Link
                    key={notification.id}
                    to={notification.href}
                    onClick={() => setOpen(false)}
                    className="flex items-start gap-2 rounded-xl px-3 py-2.5 transition hover:bg-surface-sunken"
                  >
                    <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-action" />
                    <div>
                      <p className="text-sm font-normal text-text-primary">
                        {notification.title}
                      </p>
                      <p className="text-xs text-text-muted">
                        {notification.description}
                      </p>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}

          <Link
            to={ROUTES.ATHLETE.HOME}
            onClick={() => setOpen(false)}
            className="mt-1 block rounded-xl px-3 py-2.5 text-center text-sm font-light text-brand-action hover:bg-surface-sunken hover:text-brand-action-hover"
          >
            View all notifications
          </Link>
        </div>
      )}
    </div>
  );
}

export default function AthleteLayout() {
  const { user, signOut } = useAuth();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const { notifications } = useAthleteNotifications();

  return (
    <div className="min-h-screen bg-surface-card">
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
              <IconButton
                icon={Menu}
                label="Open menu"
                onClick={() => setMobileNavOpen(true)}
                className="lg:hidden"
              />

              <div>
                <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.08em] text-text-muted">
                  Performance Centre
                </p>
                <p className="mt-1 truncate text-sm font-semibold text-text-secondary">
                  {user?.email}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <IconButton icon={Upload} label="Upload a performance" to={ROUTES.ATHLETE.NEW_PERFORMANCE} />

              <NotificationsMenu notifications={notifications} />

              <UserMenu />
            </div>
          </div>
        </header>

        <div className="px-6 py-8 lg:px-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
