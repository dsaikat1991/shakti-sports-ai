export default function AuthDivider() {
  return (
    <div className="my-6 flex items-center gap-4">
      <div className="h-px flex-1 bg-gray-200" />
      <span className="font-['JetBrains_Mono'] text-[10px] font-semibold uppercase tracking-[0.2em] text-gray-400">
        or
      </span>
      <div className="h-px flex-1 bg-gray-200" />
    </div>
  );
}