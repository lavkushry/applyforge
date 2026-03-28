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
    refetchInterval: (query) => {
      const status = (query.state.data as RunDetail | undefined)?.run.status;
      return status && ["queued", "running"].includes(status) ? 3000 : false;
    },
  });
  const run = runQuery.data;
  const handoffSteps =
    run?.steps.filter(
      (step) =>
        step.requires_approval ||
        step.step_kind === "anti_bot" ||
        step.name === "manual_question_review_required" ||
        step.name === "unsupported_fields_detected",
    ) || [];

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
              <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                <div className="flex flex-wrap items-center gap-3">
                  <Badge>{run.run.mode}</Badge>
                  <Badge>{run.run.status}</Badge>
                  <Badge tone="default">{run.run.current_step}</Badge>
                </div>
                <p className="mt-3 text-sm text-slate-300">Task ID: {run.run.external_task_id || "Not dispatched"}</p>
                {run.run.error_message ? <p className="mt-2 text-sm text-rose-300">{run.run.error_message}</p> : null}
              </div>
              {handoffSteps.length ? (
                <Card className="border-amber-400/30 bg-amber-500/10">
                  <h2 className="text-base font-semibold text-white">Manual handoff required</h2>
                  <div className="mt-3 space-y-3">
                    {handoffSteps.map((step) => (
                      <div key={step.id} className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge tone="warning">{step.step_kind}</Badge>
                          <Badge>{step.name}</Badge>
                        </div>
                        <p className="mt-2 text-sm text-slate-200">
                          {String((step.output && step.output.reason) || "This step needs manual review before the run can continue.")}
                        </p>
                      </div>
                    ))}
                  </div>
                </Card>
              ) : null}
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
                  {step.screenshot_file_id ? (
                    <a
                      className="mt-3 inline-flex text-sm text-cyan-300"
                      href={`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/files/${step.screenshot_file_id}`}
                      rel="noreferrer"
                      target="_blank"
                    >
                      Open screenshot
                    </a>
                  ) : null}
                  <pre className="mt-3 overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
                    {JSON.stringify(
                      Object.keys(step.masked_output || {}).length ? step.masked_output : step.output,
                      null,
                      2,
                    )}
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
