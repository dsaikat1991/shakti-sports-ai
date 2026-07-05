export default function Loader({ label = "Loading..." }) {
  return (
    <div className="flex items-center gap-3 text-slate-400">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
      <span>{label}</span>
    </div>
  );
}