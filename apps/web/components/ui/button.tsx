import { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
};

const variants = {
  primary: "bg-cyan-400 text-slate-950 hover:bg-cyan-300",
  secondary: "bg-slate-800 text-slate-100 hover:bg-slate-700",
  ghost: "bg-transparent text-slate-200 hover:bg-white/5",
  danger: "bg-rose-500 text-white hover:bg-rose-400",
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-60",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}
