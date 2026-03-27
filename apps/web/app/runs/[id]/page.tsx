"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { RunDetail } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export default function RunViewPage() {
  const { id } = useParams<{ id: string }>();
  const session = useSession();
  const runQuery = useQuery({
    queryKey: ["run", id],
    queryFn: () => api<RunDetail>(`/application-runs/${id}`),
    enabled: Boolean(session.user),
  });
  const run = runQuery.data;

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Automation Timeline"
          title={run ? `Run #${run.run.id} · ${run.run.status}` : "Loading automation run…"}
          description="Every automation step is persisted with status, timestamps, and structured outputs so failures stay actionable."
        />

        <Card className="space-y-4">
          {run ? (
            <div className="space-y-4">
              {run.steps.map((step) => (
                <div key={step.id} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-medium text-white">{step.name}</p>
                      <p className="text-xs text-slate-400">{formatDate(step.started_at)}</p>
                    </div>
                    <Badge
                      tone={
                        step.status === "completed"
                          ? "success"
                          : step.status === "paused"
                            ? "warning"
                            : step.status === "failed"
                              ? "danger"
                              : "default"
                      }
                    >
                      {step.status}
                    </Badge>
                  </div>
                  <pre className="mt-3 overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
                    {JSON.stringify(step.output, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-300">Loading run timeline…</p>
          )}
        </Card>
      </section>
    </ProtectedPage>
  );
}
