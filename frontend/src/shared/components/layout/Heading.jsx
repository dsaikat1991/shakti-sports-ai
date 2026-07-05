export default function Heading({
  eyebrow,
  title,
  description,
  align = "left",
}) {
  const alignment =
    align === "center" ? "mx-auto text-center" : "text-left";

  return (
    <div className={`max-w-3xl ${alignment}`}>
      {eyebrow && (
        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.35em] text-cyan-400">
          {eyebrow}
        </p>
      )}

      <h2 className="text-4xl font-black leading-tight text-white md:text-6xl">
        {title}
      </h2>

      {description && (
        <p className="mt-6 text-lg leading-8 text-slate-400">
          {description}
        </p>
      )}
    </div>
  );
}