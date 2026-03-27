"use client";

import { useRouter } from "next/navigation";
import { ReactNode, useEffect } from "react";

import { useSession } from "@/hooks/use-session";

export function ProtectedPage({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { isLoading, user } = useSession();

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/signin");
    }
  }, [isLoading, router, user]);

  if (isLoading || !user) {
    return (
      <div className="rounded-3xl border border-white/10 bg-slate-900/60 p-10 text-center text-slate-300">
        Loading your workspace…
      </div>
    );
  }

  return <>{children}</>;
}
