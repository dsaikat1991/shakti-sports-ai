import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { navigationLinks } from "../../constants/navigation";
import { ROLE_NAVIGATION } from "../../constants/roleNavigation";
import { ROUTES } from "../../constants/routes";
import { useAuth } from "../../features/auth/context/AuthContext";
import Container from "../ui/Container";
import Logo from "../shared/Logo";
import UserMenu from "./UserMenu";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { user } = useAuth();

  const isLoggedIn = Boolean(user);

  // For now, every authenticated user is treated as athlete.
  // Later we’ll read role from profiles table.
  const roleLinks = ROLE_NAVIGATION.athlete;

  const logoHref = isLoggedIn ? ROUTES.ATHLETE.HOME : ROUTES.HOME;

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200/70 bg-white/85 backdrop-blur-xl">
      <Container>
        <nav className="flex h-20 items-center justify-between">
          <Link to={logoHref}>
            <Logo />
          </Link>

          <div className="hidden items-center gap-9 lg:flex">
            {isLoggedIn
              ? roleLinks.map((item) => (
                  <Link
                    key={item.label}
                    to={item.href}
                    className="text-sm font-bold text-gray-700 transition hover:text-[#F0600E]"
                  >
                    {item.label}
                  </Link>
                ))
              : navigationLinks.map((item) => (
                  <a
                    key={item.label}
                    href={item.href}
                    className="text-sm font-medium text-gray-600 transition hover:text-orange-600"
                  >
                    {item.label}
                  </a>
                ))}
          </div>

          <div className="hidden items-center gap-3 lg:flex">
            {isLoggedIn ? (
              <UserMenu />
            ) : (
              <>
                <Link
                  to={ROUTES.AUTH.SIGN_IN}
                  className="cursor-pointer text-sm font-semibold text-gray-700 transition hover:text-orange-600"
                >
                  Sign In
                </Link>

                <Link
                  to={ROUTES.AUTH.SIGN_UP}
                  className="cursor-pointer rounded-xl bg-[#F0600E] px-5 py-2.5 text-sm font-bold text-white transition hover:bg-orange-700"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>

          <button
            type="button"
            className="inline-flex items-center justify-center rounded-lg border border-gray-200 p-2 text-gray-700 lg:hidden"
            onClick={() => setIsOpen((value) => !value)}
            aria-label="Toggle navigation"
          >
            {isOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </nav>

        {isOpen && (
          <div className="border-t border-gray-200 py-5 lg:hidden">
            <div className="flex flex-col gap-4">
              {isLoggedIn
                ? roleLinks.map((item) => (
                    <Link
                      key={item.label}
                      to={item.href}
                      onClick={() => setIsOpen(false)}
                      className="text-base font-semibold text-gray-700"
                    >
                      {item.label}
                    </Link>
                  ))
                : navigationLinks.map((item) => (
                    <a
                      key={item.label}
                      href={item.href}
                      onClick={() => setIsOpen(false)}
                      className="text-base font-medium text-gray-700"
                    >
                      {item.label}
                    </a>
                  ))}

              {!isLoggedIn && (
                <div className="mt-4 flex flex-col gap-3">
                  <Link
                    to={ROUTES.AUTH.SIGN_IN}
                    onClick={() => setIsOpen(false)}
                    className="rounded-lg border border-gray-200 px-5 py-3 text-sm font-semibold text-gray-700"
                  >
                    Sign In
                  </Link>

                  <Link
                    to={ROUTES.AUTH.SIGN_UP}
                    onClick={() => setIsOpen(false)}
                    className="rounded-lg bg-[#F0600E] px-5 py-3 text-sm font-bold text-white"
                  >
                    Get Started
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </Container>
    </header>
  );
}