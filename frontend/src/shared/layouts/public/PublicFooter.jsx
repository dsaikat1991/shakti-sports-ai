import logo from "@/assets/brand/logo.svg";
import { APP } from "@/shared/config/app";

const footerLinks = [
  {
    title: "Product",
    links: ["AI Analysis", "Athlete Profiles", "Coach Dashboard", "Scout Network"],
  },
  {
    title: "Company",
    links: ["Mission", "About", "Contact", "Careers"],
  },
  {
    title: "Resources",
    links: ["FAQ", "Privacy", "Terms", "Support"],
  },
];

export default function PublicFooter() {
  return (
    <footer className="border-t border-white/10 bg-[#050816] px-6">
      <div className="mx-auto grid max-w-7xl gap-12 py-16 md:grid-cols-2 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <img src={logo} alt={APP.NAME} className="h-11 w-auto" />

          <p className="mt-6 max-w-md leading-7 text-slate-400">
            Building India&apos;s AI-powered talent discovery platform for
            athletes, coaches, scouts and academies.
          </p>

          <p className="mt-6 text-sm text-slate-500">
            Made in India 🇮🇳
          </p>
        </div>

        {footerLinks.map((group) => (
          <div key={group.title}>
            <h3 className="font-bold text-white">{group.title}</h3>

            <ul className="mt-5 space-y-3 text-sm text-slate-400">
              {group.links.map((link) => (
                <li key={link}>
                  <a href="#" className="transition hover:text-white">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="border-t border-white/10 py-6 text-center text-sm text-slate-500">
        {APP.COPYRIGHT}
      </div>
    </footer>
  );
}