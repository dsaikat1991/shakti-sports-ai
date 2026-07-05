import { cn } from "@/shared/utils/cn";

export default function Stack({
  children,
  gap = "md",
  className = "",
}) {
  const gaps = {
    sm: "gap-2",
    md: "gap-4",
    lg: "gap-6",
    xl: "gap-10",
  };

  return (
    <div className={cn("flex flex-col", gaps[gap], className)}>
      {children}
    </div>
  );
}