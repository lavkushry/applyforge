"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { Job, JobScore } from "@/lib/types";

export default function ScoreDetailPage() {
  const { id } = useParams<{ id: string }>();
  const session = useSession();
  const jobQuery = useQuery({
    queryKey: ["job", id],
    queryFn: () => api<Job>(`/jobs/${id}`),
    enabled: Boolean(session.user),
  });
  const scoreMutation = useMutation({
    mutationFn: () => api<JobScore>(`/jobs/${id}/score`, { method: "POST" }),
  });

  const score = scoreMutation.data;

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Match Scoring"
          title={jobQuery.data ? `${jobQuery.data.title} fit analysis` : "Loading score detail…"}
          description="Score job fit across role alignment, skill overlap, seniority, and must-have requirement gaps."
        />

        <Card className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">Generate or refresh the latest score snapshot for this role.</p>
            </div>
            <Button onClick={() => scoreMutation.mutate()}>{scoreMutation.isPending ? "Scoring…" : "Refresh score"}</Button>
          </div>

          {score ? (
            <div className="space-y-5">
              <div className="flex items-center gap-3">
                <p className="text-5xl font-semibold text-white">{Math.round(score.overall_score)}</p>
                <Badge tone={score.recommendation === "high priority" ? "success" : score.recommendation === "maybe" ? "warning" : "danger"}>
                  {score.recommendation}
                </Badge>
              </div>

              <Card className="space-y-3 border-white/5 bg-slate-950/60">
                <h2 className="text-base font-semibold text-white">Breakdown</h2>
                <div className="grid gap-3 lg:grid-cols-2">
                  {Object.entries(score.score_breakdown)
                    .filter(([key]) =>
                      [
                        "title_fit",
                        "must_have_fit",
                        "nice_to_have_fit",
                        "location_fit",
                        "compensation_fit",
                        "visa_fit",
                        "application_readiness",
                      ].includes(key),
                    )
                    .map(([key, value]) => (
                      <div key={key} className="rounded-2xl border border-white/10 bg-slate-950/50 p-3">
                        <p className="text-xs uppercase tracking-[0.22em] text-slate-500">{key.replaceAll("_", " ")}</p>
                        <p className="mt-1 text-lg font-semibold text-white">{Math.round(value)}</p>
                      </div>
                    ))}
                </div>
                <p className="text-xs text-slate-500">Enrichment revision {score.enrichment_revision}</p>
              </Card>

              <div className="grid gap-4 lg:grid-cols-2">
                <Card className="space-y-3 border-white/5 bg-slate-950/60">
                  <h2 className="text-base font-semibold text-white">Strengths</h2>
                  <ul className="space-y-2 text-sm text-slate-300">
                    {score.strengths.map((strength) => (
                      <li key={strength}>• {strength}</li>
                    ))}
                  </ul>
                </Card>
                <Card className="space-y-3 border-white/5 bg-slate-950/60">
                  <h2 className="text-base font-semibold text-white">Missing skills</h2>
                  <ul className="space-y-2 text-sm text-slate-300">
                    {score.missing_skills.map((skill) => (
                      <li key={skill}>• {skill}</li>
                    ))}
                  </ul>
                </Card>
              </div>

              <Card className="space-y-3 border-white/5 bg-slate-950/60">
                <h2 className="text-base font-semibold text-white">Why this score</h2>
                <ul className="space-y-2 text-sm text-slate-300">
                  {score.reasons.map((reason) => (
                    <li key={reason}>• {reason}</li>
                  ))}
                </ul>
              </Card>
            </div>
          ) : (
            <p className="text-sm text-slate-300">No score yet. Generate one to inspect the breakdown.</p>
          )}
        </Card>
      </section>
    </ProtectedPage>
  );
}
