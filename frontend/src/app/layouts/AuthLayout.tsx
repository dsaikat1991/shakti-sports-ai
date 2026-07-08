import { Outlet } from "react-router-dom";
import Logo from "../../components/shared/Logo";

export default function AuthLayout() {
  return (
    <main className="min-h-screen bg-[#FAFAF7] px-6 py-8">
      <div className="mx-auto flex min-h-[calc(100vh-64px)] max-w-6xl flex-col">
        <Logo />

        <div className="flex flex-1 items-center justify-center py-12">
          <Outlet />
        </div>
      </div>
    </main>
  );
}