import { cn } from "@/lib/utils";

export function Badge({
  children,
  tone = "default",
}: {
  children: React.ReactNode;
  tone?: "default" | "success" | "warning" | "danger";
}) {
  const toneClass =
    tone === "success"
      ? "bg-emerald-500/10 text-emerald-200"
      : tone === "warning"
        ? "bg-amber-500/10 text-amber-100"
        : tone === "danger"
          ? "bg-rose-500/10 text-rose-100"
          : "bg-cyan-500/10 text-cyan-100";

  return <span className={cn("rounded-full px-3 py-1 text-xs font-medium", toneClass)}>{children}</span>;
}
