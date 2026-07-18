export type ErrorContext = "upload" | "analysis" | "dashboard";

// The Design Bible's four-beat error formula ((1) what happened, plainly
// (2) why, only if it helps (3) what to do next, specific and doable
// (4) reassurance that this is normal and fixable), applied wherever a raw
// system/network error string would otherwise reach a user. Scoped to the
// athlete upload/analysis flow for now (ReviewStep, PerformanceProcessing,
// AthleteHome) - not yet applied to the other raw error.message call sites
// across the app.
export function friendlyErrorMessage(error: unknown, context: ErrorContext): string {
  const raw = error instanceof Error ? error.message : String(error ?? "");
  const lower = raw.toLowerCase();

  if (
    lower.includes("session has expired") ||
    lower.includes("jwt") ||
    lower.includes("not authenticated")
  ) {
    return "You've been signed out. Sign in again and we'll pick up right where you left off.";
  }

  if (
    lower.includes("network") ||
    lower.includes("fetch") ||
    lower.includes("connection")
  ) {
    return "We couldn't reach the server. Check your connection and try again - this is usually quick to fix.";
  }

  switch (context) {
    case "upload":
      return "Your recording didn't upload this time. Check your connection and try again - your details are still saved, so you won't need to start over.";
    case "analysis":
      return "We couldn't finish analyzing this recording. Your video is safe - try again, or come back to it later.";
    case "dashboard":
      return "We couldn't load your dashboard just now. Try refreshing the page in a moment.";
    default:
      return "Something didn't work as expected. Try again in a moment.";
  }
}
