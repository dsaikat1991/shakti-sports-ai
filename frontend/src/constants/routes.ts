import type { UserRole } from "../features/auth/types/auth";

export const ROUTES = {
  HOME: "/",

  AUTH: {
    SIGN_IN: "/signin",
    SIGN_UP: "/signup",
    CHOOSE_ROLE: "/choose-role",
    ATHLETE_ONBOARDING: "/onboarding/athlete",
    COACH_ONBOARDING: "/onboarding/coach",
    ACADEMY_ONBOARDING: "/onboarding/academy",
  },

  ATHLETE: {
    HOME: "/console/athlete",

    NEW_PERFORMANCE: "/console/athlete/performances/new",

    HISTORY: "/console/athlete/performances",

    PROFILE: "/console/athlete/profile",

    SETTINGS: "/console/athlete/settings",

    PERFORMANCE_PROCESSING: (id: string) =>
      `/console/athlete/performances/${id}/processing`,

    PERFORMANCE_REPORT: (id: string) =>
      `/console/athlete/performances/${id}`,

    PERFORMANCE_EDIT: (id: string) =>
      `/console/athlete/performances/${id}/edit`,
  },

  COACH: {
    HOME: "/console/coach",
  },

  ACADEMY: {
    HOME: "/console/academy",
  },
} as const;

// role === null covers a user who has authenticated but not yet finished
// onboarding (no profiles row exists yet) - send them to choose-role
// rather than assuming a console they haven't picked yet.
export function roleHomeRoute(role: UserRole | null): string {
  switch (role) {
    case "athlete":
      return ROUTES.ATHLETE.HOME;
    case "coach":
      return ROUTES.COACH.HOME;
    case "academy":
      return ROUTES.ACADEMY.HOME;
    case "admin":
      return ROUTES.ATHLETE.HOME; // no admin console exists yet
    default:
      return ROUTES.AUTH.CHOOSE_ROLE;
  }
}