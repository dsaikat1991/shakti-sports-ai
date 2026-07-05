import clsx from "clsx";

export default function Section({ children, className = "" }) {
  return (
    <section className={clsx("relative py-24 md:py-32", className)}>
      {children}
    </section>
  );
}