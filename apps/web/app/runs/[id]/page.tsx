"use client";
/* eslint-disable @next/next/no-img-element */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { useAppStore } from "@/store/app-store";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { ApplicationRun, RunDetail } from "@/lib/types";
import { formatDate } from "@/lib/utils";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function RunViewPage() {
  const { id } = useParams<{ id: string }>();
  const session = useSession();
  const queryClient = useQueryClient();
  const pushToast = useAppStore((state) => state.pushToast);
  const runQuery = useQuery({
    queryKey: ["run", id],
    queryFn: () => api<RunDetail>(`/application-runs/${id}`),
    enabled: Boolean(session.user),
    refetchInterval: (query) => {
      const status = (query.state.data as RunDetail | undefined)?.run.status;
      return status && ["queued", "running"].includes(status) ? 3000 : false;
    },
  });
  const resumeMutation = useMutation({
    mutationFn: (runId: number) => api<ApplicationRun>(`/application-runs/${runId}/resume`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["run", id] });
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      queryClient.invalidateQueries({ queryKey: ["applications-dashboard"] });
      pushToast({ title: "Run resumed", tone: "success" });
    },
    onError: () => pushToast({ title: "Could not resume run", tone: "error" }),
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
                  {["paused", "uncertain", "failed"].includes(run.run.status) && run.run.mode !== "draft" ? (
                    <Button
                      disabled={resumeMutation.isPending}
                      onClick={() => resumeMutation.mutate(run.run.id)}
                      variant="secondary"
                    >
                      {resumeMutation.isPending ? "Resuming…" : "Resume run"}
                    </Button>
                  ) : null}
                </div>
                <p className="mt-3 text-sm text-slate-300">Task ID: {run.run.external_task_id || "Not dispatched"}</p>
                {typeof run.run.retry_metadata?.attempt_count === "number" ? (
                  <p className="mt-2 text-sm text-slate-300">
                    Attempts {String(run.run.retry_metadata.attempt_count)} / {String(run.run.retry_metadata.max_retries ?? 0)}
                    {run.run.retry_metadata.last_retry_delay_seconds
                      ? ` · last backoff ${String(run.run.retry_metadata.last_retry_delay_seconds)}s`
                      : ""}
                  </p>
                ) : null}
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
                    <div className="mt-3 space-y-3">
                      <a
                        className="inline-flex text-sm text-cyan-300"
                        href={`${API_BASE}/files/${step.screenshot_file_id}`}
                        rel="noreferrer"
                        target="_blank"
                      >
                        Open screenshot
                      </a>
                      <img
                        alt={`${step.name} screenshot`}
                        className="max-h-80 w-full rounded-2xl border border-white/10 object-cover"
                        src={`${API_BASE}/files/${step.screenshot_file_id}`}
                      />
                    </div>
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
