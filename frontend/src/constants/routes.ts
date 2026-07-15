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
} as const;