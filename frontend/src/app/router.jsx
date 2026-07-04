import { createBrowserRouter } from "react-router-dom";

import PublicLayout from "@/shared/layouts/public/PublicLayout";

const router = createBrowserRouter([
  {
    path: "/",
    element: <PublicLayout />,
  },
]);

export default router;