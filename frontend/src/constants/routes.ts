import type { UserRole } from "../features/auth/types/auth";

export const ROUTES = {
  HOME: "/",
  ABOUT: "/about",
  MISSION: "/mission",
  CONTACT: "/contact",
  TERMS: "/terms",
  PRIVACY: "/privacy",

  // Footer links with no real destination yet (see docs/ENGINEERING_HANDOFF.md).
  // Routed to a ComingSoon placeholder instead of a dead href="#".
  COMING_SOON: {
    AI_ANALYSIS: "/ai-analysis",
    RECORDING_GUIDE: "/recording-guide",
    FOR_ACADEMIES: "/for-academies",
  },

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

    COACHES: "/console/athlete/coaches",

    PROFILE: "/console/athlete/profile",

    SETTINGS: "/console/athlete/settings",

    PROGRESS: "/console/athlete/progress",

    GOALS: "/console/athlete/goals",

    REPORTS: "/console/athlete/reports",

    PERFORMANCE_PROCESSING: (id: string) =>
      `/console/athlete/performances/${id}/processing`,

    PERFORMANCE_REPORT: (id: string) =>
      `/console/athlete/performances/${id}`,

    PERFORMANCE_EDIT: (id: string) =>
      `/console/athlete/performances/${id}/edit`,
  },

  COACH: {
    HOME: "/console/coach",
    ATHLETES: "/console/coach/athletes",
    REQUESTS: "/console/coach/requests",
    PROFILE: "/console/coach/profile",
    SETTINGS: "/console/coach/settings",
    ATHLETE_DETAIL: (id: string) => `/console/coach/athletes/${id}`,
    DISCOVER: "/console/coach/discover",
    BOOKMARKS: "/console/coach/bookmarks",
    LISTS: "/console/coach/lists",
    LIST_DETAIL: (id: string) => `/console/coach/lists/${id}`,
    COMPARE: "/console/coach/compare",
    ATHLETE_PROGRESS: (id: string) => `/console/coach/athletes/${id}/progress`,
  },

  ACADEMY: {
    HOME: "/console/academy",
    ATHLETES: "/console/academy/athletes",
    REQUESTS: "/console/academy/requests",
    PROFILE: "/console/academy/profile",
    SETTINGS: "/console/academy/settings",
    ATHLETE_DETAIL: (id: string) => `/console/academy/athletes/${id}`,
    DISCOVER: "/console/academy/discover",
    BOOKMARKS: "/console/academy/bookmarks",
    LISTS: "/console/academy/lists",
    LIST_DETAIL: (id: string) => `/console/academy/lists/${id}`,
    COMPARE: "/console/academy/compare",
    ATHLETE_PROGRESS: (id: string) => `/console/academy/athletes/${id}/progress`,
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