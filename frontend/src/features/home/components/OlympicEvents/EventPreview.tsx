import { CheckCircle2, XCircle } from "lucide-react";

type Props = {
  quality: number;
  good: readonly string[];
  poor: readonly string[];
};

// A deliberately dark "device screen" mockup embedded in an otherwise
// light page (the recording-preview illustration), not a themed surface -
// most colors here have no light-mode token equivalent and are kept raw
// on purpose (same exception as the modal-scrim overlay elsewhere in this
// app). Only the outer card's border/shadow (which sit against the real
// page background) and the one spot using the exact brand hex are
// tokenized.
export default function EventPreview({ quality, good, poor }: Props) {
  return (
    <div className="rounded-4xl border border-border-default bg-gray-950 p-5 text-white shadow-2xl shadow-border-default">
      <div className="rounded-3xl border border-white/10 bg-white/4 p-5">
        <p className="font-['JetBrains_Mono'] text-xs uppercase tracking-[0.2em] text-orange-400">
          Recording Preview
        </p>

        <div className="mt-6 rounded-2xl border border-white/10 bg-black/30 p-5">
          <div className="flex items-center justify-between">
            <div className="h-14 w-9 rounded-xl border-2 border-orange-400" />
            <div className="h-px flex-1 bg-white/10" />
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-action font-bold">
              ATH
            </div>
            <div className="h-px flex-1 bg-white/10" />
            <div className="rounded-full border border-white/20 px-3 py-1 text-xs text-white/60">
              Track
            </div>
          </div>

          <div className="mt-5 rounded-xl border border-dashed border-white/20 p-4 text-center text-xs text-white/50">
            Keep the athlete full-body in frame for the entire movement.
          </div>
        </div>

        <div className="mt-5">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-sm font-bold">AI Detection Quality</p>
            <p className="font-['JetBrains_Mono'] text-sm text-orange-400">
              {quality}%
            </p>
          </div>

          <div className="h-2 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-brand-action"
              style={{ width: `${quality}%` }}
            />
          </div>
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/4 p-4">
            <p className="text-sm font-bold text-green-300">Good Recording</p>

            <div className="mt-3 space-y-2">
              {good.map((item) => (
                <div key={item} className="flex items-center gap-2 text-sm text-white/70">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/4 p-4">
            <p className="text-sm font-bold text-red-300">Poor Recording</p>

            <div className="mt-3 space-y-2">
              {poor.map((item) => (
                <div key={item} className="flex items-center gap-2 text-sm text-white/70">
                  <XCircle className="h-4 w-4 text-red-400" />
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}