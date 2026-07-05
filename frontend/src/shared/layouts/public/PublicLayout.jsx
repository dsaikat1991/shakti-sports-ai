import { Outlet } from "react-router-dom";

import PublicFooter from "./PublicFooter";
import PublicNavbar from "./PublicNavbar";

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-[#050816] text-white">
      <PublicNavbar />

      <Outlet />

      <PublicFooter />
    </div>
  );
}