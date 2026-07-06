import { Menu, X } from "lucide-react";
import { useState } from "react";
import Logo from "../shared/Logo";
import Button from "../ui/Button";
import Container from "../ui/Container";
import { navigationLinks } from "../../constants/navigation";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200/70 bg-white/85 backdrop-blur-xl">
      <Container>
        <nav className="flex h-20 items-center justify-between">
          <Logo />

          <div className="hidden items-center gap-9 lg:flex">
            {navigationLinks.map((item) => (
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
            <button className="cursor-pointer text-sm font-semibold text-gray-700 transition hover:text-orange-600">
              Sign In
            </button>

            <Button className="cursor-pointer px-5 py-2.5">Upload Video</Button>
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
              {navigationLinks.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className="text-base font-medium text-gray-700"
                >
                  {item.label}
                </a>
              ))}

              <div className="mt-4 flex flex-col gap-3">
                <button className="rounded-lg border border-gray-200 px-5 py-3 text-left text-sm font-semibold text-gray-700">
                  Sign In
                </button>

                <Button>Upload Video</Button>
              </div>
            </div>
          </div>
        )}
      </Container>
    </header>
  );
}