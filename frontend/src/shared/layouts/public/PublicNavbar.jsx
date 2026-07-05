import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import logo from "@/assets/brand/logo.svg";
import { Button } from "@/shared/components";
import { ROUTES } from "@/shared/config/routes";

const navItems = [
  { label: "Athletes", href: "#athletes" },
  { label: "Academies", href: "#academies" },
  { label: "Scouts", href: "#scouts" },
  { label: "About", href: "#about" },
];

export default function PublicNavbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#050816]/80 backdrop-blur-xl">
      <nav className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">
        <Link to={ROUTES.HOME} className="flex items-center">
          <img
            src={logo}
            alt="Shakti Sports AI"
            className="h-10 w-auto"
          />
        </Link>

        <div className="hidden items-center gap-8 text-sm font-medium text-slate-300 lg:flex">
          {navItems.map((item) => (
            <a key={item.label} href={item.href} className="transition hover:text-white">
              {item.label}
            </a>
          ))}
        </div>

        <div className="hidden items-center gap-4 lg:flex">
          <Link
            to={ROUTES.LOGIN}
            className="text-sm font-medium text-slate-300 transition hover:text-white"
          >
            Login
          </Link>

          <Button size="sm">Get AI Analysis</Button>
        </div>

        <button
          onClick={() => setIsOpen((value) => !value)}
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 text-white lg:hidden"
          aria-label="Toggle menu"
        >
          {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </nav>

      {isOpen && (
        <div className="border-t border-white/10 bg-[#050816] px-6 py-6 lg:hidden">
          <div className="flex flex-col gap-5 text-sm font-medium text-slate-300">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                onClick={() => setIsOpen(false)}
                className="transition hover:text-white"
              >
                {item.label}
              </a>
            ))}

            <Link
              to={ROUTES.LOGIN}
              onClick={() => setIsOpen(false)}
              className="transition hover:text-white"
            >
              Login
            </Link>

            <Button size="sm" className="w-full">
              Get AI Analysis
            </Button>
          </div>
        </div>
      )}
    </header>
  );
}