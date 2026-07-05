import { cn } from "@/shared/utils/cn";

export default function Grid({
  children,
  cols = 2,
  className = "",
}) {
  const layouts = {
    1: "grid-cols-1",
    2: "grid-cols-1 md:grid-cols-2",
    3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-2 lg:grid-cols-4",
  };

  return (
    <div className={cn("grid gap-6", layouts[cols], className)}>
      {children}
    </div>
  );
}