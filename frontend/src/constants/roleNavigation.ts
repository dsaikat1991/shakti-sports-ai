import { ROUTES } from "./routes";

export type UserRole = "athlete" | "coach" | "academy" | "admin";

export const ROLE_NAVIGATION = {
  athlete: [
    { label: "Dashboard", href: ROUTES.ATHLETE.HOME },
    { label: "New Performance", href: ROUTES.ATHLETE.NEW_PERFORMANCE },
  ],

  coach: [
    { label: "Dashboard", href: "/console/coach" },
    { label: "Discover Talent", href: "/console/coach/discover" },
  ],

  academy: [
    { label: "Dashboard", href: "/console/academy" },
    { label: "Manage Athletes", href: "/console/academy/athletes" },
  ],

  admin: [
    { label: "Admin Console", href: "/admin" },
  ],
} satisfies Record<UserRole, { label: string; href: string }[]>;