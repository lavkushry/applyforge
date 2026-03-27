import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const featureBlocks = [
  {
    title: "Resume intelligence",
    description: "Upload a raw resume, parse it into structured facts, and keep a master profile you can safely tailor.",
  },
  {
    title: "Job discovery and fit scoring",
    description: "Collect jobs from URLs or pasted descriptions, normalize them, and rank them against your profile.",
  },
  {
    title: "Guarded automation",
    description: "Prepare, assist, or auto-run applications with step logs, screenshots, and explicit approval pauses.",
  },
];

export default function LandingPage() {
  return (
    <section className="space-y-8">
      <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <Card className="space-y-6 overflow-hidden">
          <Badge>Production-minded MVP</Badge>
          <div className="space-y-4">
            <h2 className="max-w-3xl text-5xl font-semibold leading-tight text-white">
              Run the entire job hunt pipeline from one operating system.
            </h2>
            <p className="max-w-2xl text-base text-slate-300">
              ApplyForge helps serious candidates move from resume upload to scored opportunities, tailored documents,
              and browser-assisted application runs without losing observability or factual safety.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/signup">
              <Button>Create account</Button>
            </Link>
            <Link href="/signin">
              <Button variant="secondary">Open demo</Button>
            </Link>
          </div>
          <div className="grid gap-4 pt-4 sm:grid-cols-3">
            {[
              ["1 profile", "Canonical candidate brain"],
              ["3 modes", "Draft, assisted, and auto apply"],
              ["Step logs", "Every automation checkpoint retained"],
            ].map(([value, label]) => (
              <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-3xl font-semibold text-white">{value}</p>
                <p className="mt-2 text-sm text-slate-300">{label}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="space-y-4">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.22em] text-cyan-300">Flow</p>
            <h3 className="text-xl font-semibold text-white">From resume upload to tracked application</h3>
          </div>
          <div className="space-y-3">
            {[
              "Import a resume PDF or DOCX",
              "Parse and edit a fact-locked profile",
              "Normalize incoming job descriptions",
              "Score fit and explain tradeoffs",
              "Generate tailored resume versions",
              "Draft cover letters and application answers",
              "Run assisted or auto applications with review gates",
            ].map((item, index) => (
              <div key={item} className="flex gap-3 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-400 text-sm font-semibold text-slate-950">
                  {index + 1}
                </div>
                <p className="text-sm text-slate-200">{item}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {featureBlocks.map((feature) => (
          <Card key={feature.title} className="space-y-3">
            <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
            <p className="text-sm text-slate-300">{feature.description}</p>
          </Card>
        ))}
      </div>
    </section>
  );
}
