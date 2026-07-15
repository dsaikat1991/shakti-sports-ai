import { Link } from "react-router-dom";
import Logo from "../shared/Logo";
import { ROUTES } from "../../constants/routes";

type FooterLink = {
  label: string;
  href: string;
  external?: boolean;
};

const footerLinks: { title: string; links: FooterLink[] }[] = [
  {
    title: "Platform",
    links: [
      { label: "How it works", href: "/#how-it-works", external: true },
      { label: "AI analysis", href: ROUTES.COMING_SOON.AI_ANALYSIS },
      { label: "Recording guide", href: ROUTES.COMING_SOON.RECORDING_GUIDE },
    ],
  },
  {
    title: "Community",
    links: [
      { label: "For athletes", href: "/#athletes", external: true },
      { label: "For coaches", href: "/#coaches", external: true },
      { label: "For academies", href: ROUTES.COMING_SOON.FOR_ACADEMIES },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: ROUTES.ABOUT },
      { label: "Mission", href: ROUTES.MISSION },
      { label: "Contact", href: ROUTES.CONTACT },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white py-12">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="grid gap-10 lg:grid-cols-[1fr_1.5fr]">
          <div>
            <Logo />

            <p className="mt-4 max-w-xs text-sm leading-6 text-gray-500">
              AI-powered athlete talent discovery, built so no athlete's shot
              depends on which city they were born in.
            </p>
          </div>

          <div className="grid gap-8 sm:grid-cols-3">
            {footerLinks.map((group) => (
              <div key={group.title}>
                <h4 className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
                  {group.title}
                </h4>

                <div className="mt-4 space-y-3">
                  {group.links.map((link) =>
                    link.external ? (
                      <a
                        key={link.label}
                        href={link.href}
                        className="block text-sm font-medium text-gray-700 transition hover:text-[#F0600E]"
                      >
                        {link.label}
                      </a>
                    ) : (
                      <Link
                        key={link.label}
                        to={link.href}
                        className="block text-sm font-medium text-gray-700 transition hover:text-[#F0600E]"
                      >
                        {link.label}
                      </Link>
                    ),
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-gray-200 pt-6 text-sm text-gray-500">
          <p>© 2026 Shakti Sports AI</p>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            <Link
              to={ROUTES.TERMS}
              className="transition hover:text-[#F0600E]"
            >
              Terms of Use
            </Link>
            <Link
              to={ROUTES.PRIVACY}
              className="transition hover:text-[#F0600E]"
            >
              Privacy Policy
            </Link>
          </div>

          <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em]">
            Made in India · For the Podium
          </p>
        </div>
      </div>
    </footer>
  );
}
