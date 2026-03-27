import "./globals.css";

import type { ReactNode } from "react";

import { Nav } from "@/components/nav";
import { AppProviders } from "@/components/providers/app-providers";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProviders>
          <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.16),_transparent_28%),radial-gradient(circle_at_80%_10%,_rgba(59,130,246,0.14),_transparent_22%),linear-gradient(180deg,_#020617_0%,_#0f172a_42%,_#020617_100%)]">
            <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
              <header className="rounded-[2rem] border border-white/10 bg-slate-950/70 px-6 py-5 backdrop-blur">
                <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
                  <div className="space-y-1">
                    <p className="text-xs uppercase tracking-[0.22em] text-cyan-300">ApplyForge</p>
                    <h1 className="text-3xl font-semibold text-white">Your AI Job Hunt Operating System</h1>
                    <p className="max-w-3xl text-sm text-slate-300">
                      Resume intelligence, job scoring, tailored applications, and guarded automation in one SaaS workflow.
                    </p>
                  </div>
                </div>
                <Nav />
              </header>
              {children}
            </main>
          </div>
        </AppProviders>
      </body>
    </html>
  );
}
