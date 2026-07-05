import { createBrowserRouter } from "react-router-dom";

import { LandingPage } from "@/features/landing";
import { ROUTES } from "@/shared/config/routes";
import PublicLayout from "@/shared/layouts/public/PublicLayout";

const router = createBrowserRouter([
  {
    path: ROUTES.HOME,
    element: <PublicLayout />,
    children: [
      {
        index: true,
        element: <LandingPage />,
      },
    ],
  },
]);

export default router;