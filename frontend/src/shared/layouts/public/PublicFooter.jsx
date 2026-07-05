import { APP } from "@/shared/config/app";

export default function PublicFooter() {
  return (
    <footer className="border-t border-white/10 bg-[#050816] px-6 py-8 text-center text-sm text-slate-500">
      {APP.COPYRIGHT}
    </footer>
  );
}