import { Camera, Clock, Gauge, Ruler, Sun } from "lucide-react";

type Props = {
  camera: string;
  distance: string;
  fps: string;
  duration: string;
  lighting: string;
};

export default function RecordingGuide({
  camera,
  distance,
  fps,
  duration,
  lighting,
}: Props) {
  const guide = [
    { icon: Camera, label: "Camera", value: camera },
    { icon: Ruler, label: "Distance", value: distance },
    { icon: Gauge, label: "Frame Rate", value: fps },
    { icon: Clock, label: "Duration", value: duration },
    { icon: Sun, label: "Lighting", value: lighting },
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {guide.map((item) => {
        const Icon = item.icon;

        return (
          <div
            key={item.label}
            className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-50">
                <Icon className="h-5 w-5 text-[#F0600E]" />
              </div>

              <div>
                <p className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-widest text-gray-400">
                  {item.label}
                </p>
                <p className="mt-1 text-sm font-bold text-gray-950">
                  {item.value}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}