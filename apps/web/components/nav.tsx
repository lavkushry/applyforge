"use client";

import type { Route } from "next";
import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/app-store";

const links = [
  ["Wizard", "/wizard"],
  ["Dashboard", "/dashboard"],
  ["Resume", "/resume"],
  ["Profile", "/profile"],
  ["Roles", "/roles"],
  ["Companies", "/companies"],
  ["Jobs", "/jobs"],
  ["Applications", "/applications"],
  ["Settings", "/settings"],
  ["Admin", "/admin"],
] as const;

export function Nav() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const session = useSession();
  const pushToast = useAppStore((state) => state.pushToast);

  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <nav className="flex flex-wrap gap-2">
        {links.map(([label, href]) => (
          <Link
            key={href}
            href={href as Route}
            className={cn(
              "rounded-full border border-white/10 px-3 py-2 text-sm text-slate-300 transition hover:border-cyan-300/40 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950",
            )}
          >
            {label}
          </Link>
        ))}
      </nav>
      <div className="flex items-center gap-3">
        <p className="text-sm text-slate-400">{session.user?.email || "Guest session"}</p>
        {session.user ? (
          <Button
            variant="ghost"
            onClick={async () => {
              await api("/auth/logout", { method: "POST" });
              queryClient.setQueryData(["session"], null);
              useAppStore.getState().setSession(null);
              pushToast({ title: "Signed out", tone: "info" });
              router.replace("/signin");
            }}
          >
            Sign out
          </Button>
        ) : (
          <Link
            href="/signin"
            className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-200 transition hover:border-cyan-300/40 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
          >
            Sign in
          </Link>
        )}
      </div>
    </div>
  );
}
