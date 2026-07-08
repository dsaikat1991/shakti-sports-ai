import { BrowserRouter, Route, Routes } from "react-router-dom";
import MarketingLayout from "../layouts/MarketingLayout";
import AuthLayout from "../layouts/AuthLayout";
import HomePage from "../pages/HomePage";
import SignIn from "../../features/auth/pages/SignIn";
import SignUp from "../../features/auth/pages/SignUp";
import ProtectedRoute from "./ProtectedRoute";
import ChooseRole from "../../features/auth/pages/ChooseRole";
import AthleteOnboarding from "../../features/auth/pages/AthleteOnboarding";
import AthleteLayout from "../../features/athlete/components/AthleteLayout";
import AthleteHome from "../../features/athlete/pages/AthleteHome";
import NewPerformance from "../../features/performances/pages/NewPerformance";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MarketingLayout />}>
          <Route path="/" element={<HomePage />} />
        </Route>

        <Route element={<AuthLayout />}>
            <Route path="/signin" element={<SignIn />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/choose-role" element={<ChooseRole />} />
            <Route path="/onboarding/athlete" element={<AthleteOnboarding />} />
        </Route>

        <Route element={<ProtectedRoute />}>
  <Route path="/console/athlete" element={<AthleteLayout />}>
    <Route index element={<AthleteHome />} />

    <Route
      path="performances/new"
      element={<NewPerformance />}
    />

  </Route>
</Route>
      </Routes>
    </BrowserRouter>
  );
}