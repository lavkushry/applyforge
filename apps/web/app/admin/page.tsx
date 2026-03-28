"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { StatCard } from "@/components/ui/stat-card";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type {
  AdminEnrichmentError,
  AdminRun,
  AdminStepError,
  HealthStatus,
  InboxOtpEvent,
  IngestionRun,
} from "@/lib/types";
import { useAppStore } from "@/store/app-store";

type PromptLog = {
  id: number;
  action: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export default function AdminPage() {
  const session = useSession();
  const enabled = Boolean(session.user);
  const queryClient = useQueryClient();
  const pushToast = useAppStore((state) => state.pushToast);

  const runsQuery = useQuery({
    queryKey: ["admin-runs"],
    queryFn: () => api<AdminRun[]>("/admin/runs"),
    enabled,
  });
  const errorsQuery = useQuery({
    queryKey: ["admin-errors"],
    queryFn: () => api<AdminStepError[]>("/admin/errors"),
    enabled,
  });
  const logsQuery = useQuery({
    queryKey: ["prompt-logs"],
    queryFn: () => api<PromptLog[]>("/admin/prompt-logs"),
    enabled,
  });
  const ingestionQuery = useQuery({
    queryKey: ["ingestion-runs"],
    queryFn: () => api<IngestionRun[]>("/admin/ingestion-runs"),
    enabled,
  });
  const enrichmentErrorsQuery = useQuery({
    queryKey: ["admin-enrichment-errors"],
    queryFn: () => api<AdminEnrichmentError[]>("/admin/enrichment-errors"),
    enabled,
  });
  const otpQuery = useQuery({
    queryKey: ["otp-events"],
    queryFn: () => api<InboxOtpEvent[]>("/admin/otp-events"),
    enabled,
  });
  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: () => api<HealthStatus>("/admin/health"),
    enabled,
  });

  const refreshAdmin = () => {
    queryClient.invalidateQueries({ queryKey: ["admin-runs"] });
    queryClient.invalidateQueries({ queryKey: ["admin-errors"] });
    queryClient.invalidateQueries({ queryKey: ["admin-enrichment-errors"] });
    queryClient.invalidateQueries({ queryKey: ["ingestion-runs"] });
    queryClient.invalidateQueries({ queryKey: ["jobs"] });
    queryClient.invalidateQueries({ queryKey: ["applications"] });
    queryClient.invalidateQueries({ queryKey: ["applications-dashboard"] });
  };

  const retryRunMutation = useMutation({
    mutationFn: (runId: number) => api<{ run_id: number }>(`/admin/runs/${runId}/retry`, { method: "POST" }),
    onSuccess: () => {
      refreshAdmin();
      pushToast({ title: "Run retry queued", tone: "success" });
    },
    onError: () => pushToast({ title: "Could not retry run", tone: "error" }),
  });

  const retryEnrichmentMutation = useMutation({
    mutationFn: (jobId: number) => api<{ run_id: number }>(`/admin/jobs/${jobId}/retry-enrichment`, { method: "POST" }),
    onSuccess: () => {
      refreshAdmin();
      pushToast({ title: "Enrichment retry queued", tone: "success" });
    },
    onError: () => pushToast({ title: "Could not retry enrichment", tone: "error" }),
  });

  const runs = runsQuery.data || [];
  const stepErrors = errorsQuery.data || [];
  const ingestionRuns = ingestionQuery.data || [];
  const enrichmentErrors = enrichmentErrorsQuery.data || [];
  const otpEvents = otpQuery.data || [];
  const promptLogs = logsQuery.data || [];

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Diagnostics"
          title="Internal operations panel"
          description="Monitor queue health, recover failed enrichment jobs, inspect paused application runs, and spot OTP or prompt issues before they become support work."
        />

        <div className="grid gap-4 xl:grid-cols-4">
          <StatCard label="API health" value={healthQuery.data?.status || "unknown"} hint={`DB ${healthQuery.data?.database || "pending"} · Redis ${healthQuery.data?.redis || "pending"}`} />
          <StatCard label="Tracked runs" value={String(runs.length)} hint="Latest user-scoped automation attempts." />
          <StatCard label="Paused or failed steps" value={String(stepErrors.length)} hint="Approval gates, worker errors, or manual handoff points." />
          <StatCard label="Failed enrichments" value={String(enrichmentErrors.length)} hint="Jobs waiting for operator retry or source cleanup." />
        </div>

        <div className="grid gap-4 xl:grid-cols-2">
          <Card className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-white">Application runs</h2>
              <Badge>{runs.length}</Badge>
            </div>
            {runs.length ? (
              <div className="space-y-3">
                {runs.slice(0, 8).map((run) => (
                  <div key={run.id} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge>{run.mode}</Badge>
                        <Badge tone={["completed"].includes(run.status) ? "success" : run.status === "running" ? "warning" : "default"}>
                          {run.status}
                        </Badge>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <Link href={`/runs/${run.id}`}>
                          <Button variant="secondary">Open run</Button>
                        </Link>
                        {["paused", "uncertain", "failed"].includes(run.status) ? (
                          <Button
                            disabled={retryRunMutation.isPending}
                            onClick={() => retryRunMutation.mutate(run.id)}
                            variant="secondary"
                          >
                            Retry run
                          </Button>
                        ) : null}
                      </div>
                    </div>
                    <p className="mt-3 text-sm text-slate-300">Step: {run.current_step}</p>
                    {run.error_message ? <p className="mt-1 text-sm text-amber-200">{run.error_message}</p> : null}
                    {run.external_task_id ? (
                      <p className="mt-1 text-xs text-slate-500">Task: {run.external_task_id}</p>
                    ) : null}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No application runs yet" description="Queue an assisted or auto apply run to populate diagnostics." />
            )}
          </Card>

          <Card className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-white">Failed enrichments</h2>
              <Badge tone={enrichmentErrors.length ? "warning" : "success"}>{enrichmentErrors.length}</Badge>
            </div>
            {enrichmentErrors.length ? (
              <div className="space-y-3">
                {enrichmentErrors.slice(0, 8).map((item) => (
                  <div key={item.job_id} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <p className="text-sm font-medium text-white">{item.title}</p>
                        <p className="text-sm text-slate-400">
                          {item.company} · {item.role_name}
                        </p>
                      </div>
                      <Button
                        disabled={retryEnrichmentMutation.isPending}
                        onClick={() => retryEnrichmentMutation.mutate(item.job_id)}
                        variant="secondary"
                      >
                        Retry enrichment
                      </Button>
                    </div>
                    <p className="mt-3 text-sm text-amber-200">{item.error_message || "Unknown enrichment failure"}</p>
                    {item.application_url ? (
                      <a className="mt-2 inline-block text-sm text-cyan-300" href={item.application_url} rel="noreferrer" target="_blank">
                        Open source job link
                      </a>
                    ) : null}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No failed enrichments" description="Discovery and enrichment currently look healthy for this user." />
            )}
          </Card>
        </div>

        <div className="grid gap-4 xl:grid-cols-3">
          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Paused or failed steps</h2>
            <div className="space-y-3">
              {stepErrors.slice(0, 6).map((step) => (
                <div key={step.id} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge>{step.status}</Badge>
                    <Badge tone="warning">{step.step_kind}</Badge>
                  </div>
                  <p className="mt-2 text-sm font-medium text-white">{step.name}</p>
                  <p className="mt-2 text-sm text-slate-300">{String(step.output.reason || step.output.error || "Manual review required")}</p>
                </div>
              ))}
              {!stepErrors.length ? <EmptyState title="No paused or failed steps" description="Recent run steps look clean." /> : null}
            </div>
          </Card>

          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Ingestion runs</h2>
            <div className="space-y-3">
              {ingestionRuns.slice(0, 6).map((run) => (
                <div key={run.id} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge>{run.status}</Badge>
                    {run.role_name ? <Badge tone="default">{run.role_name}</Badge> : null}
                  </div>
                  <p className="mt-2 text-sm text-slate-300">
                    Discovered {run.discovered_count} · Enriched {run.enriched_count} · Failed {run.failed_count} · Expired {run.expired_count}
                  </p>
                  {run.error_message ? <p className="mt-2 text-sm text-amber-200">{run.error_message}</p> : null}
                </div>
              ))}
            </div>
          </Card>

          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">OTP events</h2>
            <div className="space-y-3">
              {otpEvents.slice(0, 6).map((event) => (
                <div key={event.id} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge>{event.status}</Badge>
                    {event.code_last4 ? <Badge tone="warning">***{event.code_last4}</Badge> : null}
                  </div>
                  <p className="mt-2 text-sm text-slate-300">{event.sender || "Unknown sender"}</p>
                  <p className="mt-1 text-xs text-slate-500">{event.subject_masked}</p>
                </div>
              ))}
              {!otpEvents.length ? <EmptyState title="No OTP events yet" description="OTP lookups will appear here once inbox-assisted runs are active." /> : null}
            </div>
          </Card>
        </div>

        <div className="grid gap-4 xl:grid-cols-2">
          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Prompt logs</h2>
            <pre className="overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
              {JSON.stringify(promptLogs.slice(0, 10), null, 2)}
            </pre>
          </Card>
          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Raw health snapshot</h2>
            <pre className="overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
              {JSON.stringify(healthQuery.data || {}, null, 2)}
            </pre>
          </Card>
        </div>
      </section>
    </ProtectedPage>
  );
}
