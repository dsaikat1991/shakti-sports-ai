import Button from "../../../components/ui/Button";

export default function FinalCTA() {
  return (
    <section className="bg-surface-card py-28 text-center">
      <div className="mx-auto max-w-5xl px-6">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-brand-action">
          Your first report is free
        </p>

        <h2 className="mx-auto mt-4 max-w-4xl text-3xl font-bold leading-tight text-text-primary md:text-4xl">
          The next name on the podium might be training in a field with no
          floodlights right now.
        </h2>

        <p className="mx-auto mt-5 max-w-xl text-base leading-7 text-text-secondary">
          Upload a clip today. Find out where you actually stand — and let the
          right coach find out too.
        </p>

        <div className="mt-9 flex flex-wrap justify-center gap-4">
          <Button>Upload your first clip</Button>
          <Button variant="outline">Request coach access</Button>
        </div>
      </div>
    </section>
  );
}