import { BrowserRouter, Route, Routes } from "react-router-dom";

import MarketingLayout from "../layouts/MarketingLayout";
import AuthLayout from "../layouts/AuthLayout";

import HomePage from "../pages/HomePage";
import NotFound from "../pages/NotFound";

import ProtectedRoute from "./ProtectedRoute";

import SignIn from "../../features/auth/pages/SignIn";
import SignUp from "../../features/auth/pages/SignUp";
import ChooseRole from "../../features/auth/pages/ChooseRole";
import AthleteOnboarding from "../../features/auth/pages/AthleteOnboarding";
import CoachOnboarding from "../../features/auth/pages/CoachOnboarding";
import AcademyOnboarding from "../../features/auth/pages/AcademyOnboarding";

import AthleteLayout from "../../features/athlete/components/AthleteLayout";
import AthleteHome from "../../features/athlete/pages/AthleteHome";

import NewPerformance from "../../features/performances/pages/NewPerformance";
import PerformanceProcessing from "../../features/performances/pages/PerformanceProcessing";

import PerformanceHistory from "../../features/performances/pages/PerformanceHistory";
import PerformanceDetail from "../../features/performances/pages/PerformanceDetail";

import ComingSoon from "../../components/shared/ComingSoon";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ---------------------- */}
        {/* Marketing */}
        {/* ---------------------- */}

        <Route element={<MarketingLayout />}>
          <Route path="/" element={<HomePage />} />
        </Route>

        {/* ---------------------- */}
        {/* Authentication */}
        {/* ---------------------- */}

        <Route element={<AuthLayout />}>
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/choose-role" element={<ChooseRole />} />
          <Route
            path="/onboarding/athlete"
            element={<AthleteOnboarding />}
          />
          <Route path="/onboarding/coach" element={<CoachOnboarding />} />
          <Route
            path="/onboarding/academy"
            element={<AcademyOnboarding />}
          />
        </Route>

        {/* ---------------------- */}
        {/* Protected Athlete Area */}
        {/* ---------------------- */}

<Route element={<ProtectedRoute />}>
<Route path="/console/athlete" element={<AthleteLayout />}>
  <Route index element={<AthleteHome />} />

  <Route path="performances" element={<PerformanceHistory />} />

  <Route path="performances/new" element={<NewPerformance />} />

  <Route
    path="performances/:performanceId"
    element={<PerformanceDetail />}
  />

  <Route
    path="performances/:performanceId/processing"
    element={<PerformanceProcessing />}
  />

  <Route
    path="reports"
    element={
      <ComingSoon
        title="Reports"
        description="A dedicated view of all your Shakti Motion Intelligence reports is on its way."
      />
    }
  />

  <Route
    path="progress"
    element={
      <ComingSoon
        title="Progress"
        description="Track how your performance metrics change over time, session after session."
      />
    }
  />

  <Route
    path="discover"
    element={
      <ComingSoon
        title="Discover"
        description="A place to see how you compare with athletes across India is coming soon."
      />
    }
  />

  <Route
    path="profile"
    element={
      <ComingSoon
        title="Profile"
        description="Manage your athlete profile, personal bests, and academy details here soon."
      />
    }
  />

  <Route
    path="settings"
    element={
      <ComingSoon
        title="Settings"
        description="Account and notification settings are on the way."
      />
    }
  />
</Route>
</Route>

        {/* ---------------------- */}
        {/* Fallback */}
        {/* ---------------------- */}

        <Route element={<MarketingLayout />}>
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
