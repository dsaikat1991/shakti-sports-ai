import { BrowserRouter, Route, Routes } from "react-router-dom";

import MarketingLayout from "../layouts/MarketingLayout";
import AuthLayout from "../layouts/AuthLayout";

import HomePage from "../pages/HomePage";

import ProtectedRoute from "./ProtectedRoute";

import SignIn from "../../features/auth/pages/SignIn";
import SignUp from "../../features/auth/pages/SignUp";
import ChooseRole from "../../features/auth/pages/ChooseRole";
import AthleteOnboarding from "../../features/auth/pages/AthleteOnboarding";

import AthleteLayout from "../../features/athlete/components/AthleteLayout";
import AthleteHome from "../../features/athlete/pages/AthleteHome";

import NewPerformance from "../../features/performances/pages/NewPerformance";
import PerformanceProcessing from "../../features/performances/pages/PerformanceProcessing";

import PerformanceHistory from "../../features/performances/pages/PerformanceHistory";
import PerformanceDetail from "../../features/performances/pages/PerformanceDetail";

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
</Route>
</Route>
      </Routes>
    </BrowserRouter>
  );
}