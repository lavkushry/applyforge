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
import type { Application, ApplicationRun, ApplicationsDashboard } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

const PIPELINE_STEPS: Array<{ key: keyof NonNullable<Application["pipeline"]>; label: string }> = [
  { key: "discovered", label: "Discover" },
  { key: "enriched", label: "Enrich" },
  { key: "scored", label: "Score" },
  { key: "tailored", label: "Tailor" },
  { key: "cover_letter", label: "Cover" },
  { key: "packet_ready", label: "Packet" },
  { key: "auto_ready", label: "Auto" },
];

export default function ApplicationsPage() {
  const session = useSession();
  const queryClient = useQueryClient();
  const pushToast = useAppStore((state) => state.pushToast);
  const applicationsQuery = useQuery({
    queryKey: ["applications"],
    queryFn: () => api<Application[]>("/applications"),
    enabled: Boolean(session.user),
  });
  const dashboardQuery = useQuery({
    queryKey: ["applications-dashboard"],
    queryFn: () => api<ApplicationsDashboard>("/applications/dashboard"),
    enabled: Boolean(session.user),
  });

  const refreshQueries = () => {
    queryClient.invalidateQueries({ queryKey: ["applications"] });
    queryClient.invalidateQueries({ queryKey: ["applications-dashboard"] });
    queryClient.invalidateQueries({ queryKey: ["jobs"] });
  };

  const draftMutation = useMutation({
    mutationFn: (jobId: number) => api<ApplicationRun>(`/applications/${jobId}/run-draft`, { method: "POST" }),
    onSuccess: (run) => {
      refreshQueries();
      pushToast({ title: `Draft run ${run.status}`, tone: run.status === "completed" ? "success" : "info" });
    },
    onError: () => pushToast({ title: "Draft run failed", tone: "error" }),
  });
  const assistedMutation = useMutation({
    mutationFn: (jobId: number) => api<ApplicationRun>(`/applications/${jobId}/run-assisted`, { method: "POST" }),
    onSuccess: (run) => {
      refreshQueries();
      pushToast({ title: `Assisted run ${run.status}`, tone: run.status === "queued" ? "success" : "info" });
    },
    onError: () => pushToast({ title: "Assisted run failed", tone: "error" }),
  });
  const autoMutation = useMutation({
    mutationFn: (jobId: number) => api<ApplicationRun>(`/applications/${jobId}/run-auto`, { method: "POST" }),
    onSuccess: (run) => {
      refreshQueries();
      pushToast({ title: `Auto run ${run.status}`, tone: run.status === "queued" ? "success" : "info" });
    },
    onError: () => pushToast({ title: "Auto run failed", tone: "error" }),
  });
  const resumeRunMutation = useMutation({
    mutationFn: (runId: number) => api<ApplicationRun>(`/application-runs/${runId}/resume`, { method: "POST" }),
    onSuccess: (run) => {
      refreshQueries();
      pushToast({ title: `Run ${run.id} resumed`, tone: "success" });
    },
    onError: () => pushToast({ title: "Could not resume run", tone: "error" }),
  });
  const markAppliedMutation = useMutation({
    mutationFn: (applicationId: number) => api<Application>(`/applications/${applicationId}/mark-applied`, { method: "POST" }),
    onSuccess: () => {
      refreshQueries();
      pushToast({ title: "Application marked applied", tone: "success" });
    },
    onError: () => pushToast({ title: "Could not mark applied", tone: "error" }),
  });
  const resetReadyMutation = useMutation({
    mutationFn: (applicationId: number) => api<Application>(`/applications/${applicationId}/reset-ready`, { method: "POST" }),
    onSuccess: () => {
      refreshQueries();
      pushToast({ title: "Application reset to ready", tone: "success" });
    },
    onError: () => pushToast({ title: "Could not reset application", tone: "error" }),
  });

  const applications = applicationsQuery.data || [];
  const dashboard = dashboardQuery.data;

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Apply"
          title="Application control center"
          description="Run the ApplyForge pipeline like an operator console: dry-run packet prep, assisted browser fills, or auto-apply only when the job, packet, and score are ready."
        />

        <div className="grid gap-4 lg:grid-cols-4">
          <StatCard label="Tracked" value={String(dashboard?.pipeline_counts.tracked || applications.length)} hint="Jobs that have entered the application pipeline." />
          <StatCard label="Packet ready" value={String(dashboard?.pipeline_counts.packet_ready || 0)} hint="Applications with a usable resume, answers, and apply link." />
          <StatCard label="Auto ready" value={String(dashboard?.pipeline_counts.auto_ready || 0)} hint="Applications that currently pass the stricter auto-submit gate." />
          <StatCard label="Active runs" value={String((dashboard?.run_counts.running || 0) + (dashboard?.run_counts.queued || 0))} hint="Queued or running automation attempts." />
        </div>

        <div className="grid gap-4 xl:grid-cols-3">
          <Card className="space-y-3">
            <Badge tone="default">Draft</Badge>
            <h2 className="text-lg font-semibold text-white">Prepare everything without opening a browser</h2>
            <p className="text-sm text-slate-300">
              Equivalent to a pipeline dry run: packet review, answer resolution, and document readiness with no site interaction.
            </p>
          </Card>
          <Card className="space-y-3">
            <Badge tone="warning">Assisted</Badge>
            <h2 className="text-lg font-semibold text-white">Fill forms and stop before submit</h2>
            <p className="text-sm text-slate-300">
              The worker opens the application, fills supported fields, uploads the tailored resume, and pauses for a human decision.
            </p>
          </Card>
          <Card className="space-y-3">
            <Badge tone="success">Auto</Badge>
            <h2 className="text-lg font-semibold text-white">Submit only when policy allows it</h2>
            <p className="text-sm text-slate-300">
              Auto mode is still gated by score freshness, enrichment completeness, and approval-sensitive answers.
            </p>
          </Card>
        </div>

        {applications.length ? (
          <div className="space-y-4">
            {applications.map((application) => (
              <Card key={application.id} className="space-y-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-lg font-semibold text-white">{application.job?.title || `Job #${application.job_id}`}</h2>
                      <Badge>{application.status}</Badge>
                      {application.latest_run ? <Badge tone="warning">{application.latest_run.status}</Badge> : null}
                      {application.job?.latest_score ? <Badge tone="success">{Math.round(application.job.latest_score)} match</Badge> : null}
                    </div>
                    <p className="text-sm text-slate-400">{application.job?.company || "Unknown company"}</p>
                    <div className="flex flex-wrap gap-2">
                      {PIPELINE_STEPS.map((step) => (
                        <Badge
                          key={step.key}
                          tone={application.pipeline?.[step.key] ? "success" : step.key === "auto_ready" ? "default" : "warning"}
                        >
                          {step.label}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Link href={`/jobs/${application.job_id}`}>
                      <Button variant="secondary">View job</Button>
                    </Link>
                    {application.latest_run ? (
                      <Link href={`/runs/${application.latest_run.id}`}>
                        <Button variant="secondary">View run</Button>
                      </Link>
                    ) : null}
                    {application.latest_run &&
                    ["paused", "uncertain", "failed"].includes(application.latest_run.status) &&
                    application.latest_run.mode !== "draft" ? (
                      <Button
                        disabled={resumeRunMutation.isPending}
                        onClick={() => resumeRunMutation.mutate(application.latest_run!.id)}
                        variant="secondary"
                      >
                        {resumeRunMutation.isPending ? "Resuming…" : "Resume run"}
                      </Button>
                    ) : null}
                  </div>
                </div>

                <div className="grid gap-3 lg:grid-cols-[1.1fr_0.9fr]">
                  <div className="space-y-2 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                    <p className="text-sm text-slate-300">
                      Enrichment status: <span className="font-medium text-white">{application.job?.enrichment_status || "unknown"}</span>
                    </p>
                    <p className="text-sm text-slate-300">
                      Recommendation: <span className="font-medium text-white">{application.job?.latest_recommendation || "unscored"}</span>
                    </p>
                    {application.latest_run ? (
                      <p className="text-sm text-slate-300">
                        Latest run:{" "}
                        <span className="font-medium text-white">
                          {application.latest_run.mode} · {application.latest_run.status} · {application.latest_run.current_step}
                        </span>
                      </p>
                    ) : (
                      <p className="text-sm text-slate-400">No automation run yet.</p>
                    )}
                    {application.packet_summary?.blocking_issues?.length ? (
                      <p className="text-sm text-amber-200">Blocking issues: {application.packet_summary.blocking_issues.join(", ")}</p>
                    ) : null}
                    {application.action_required ? (
                      <div className="rounded-2xl border border-amber-400/30 bg-amber-500/10 p-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge tone="warning">{application.action_required.step_kind}</Badge>
                          <Badge>{application.action_required.name}</Badge>
                        </div>
                        <p className="mt-2 text-sm text-amber-100">{application.action_required.reason}</p>
                      </div>
                    ) : null}
                  </div>

                  <div className="flex flex-wrap items-start gap-2 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                    <Button disabled={draftMutation.isPending} onClick={() => draftMutation.mutate(application.job_id)} variant="secondary">
                      {draftMutation.isPending ? "Preparing…" : "Draft run"}
                    </Button>
                    <Button disabled={assistedMutation.isPending} onClick={() => assistedMutation.mutate(application.job_id)}>
                      {assistedMutation.isPending ? "Queueing…" : "Assisted apply"}
                    </Button>
                    <Button disabled={autoMutation.isPending} onClick={() => autoMutation.mutate(application.job_id)} variant="secondary">
                      {autoMutation.isPending ? "Queueing…" : "Auto apply"}
                    </Button>
                    <Button
                      disabled={markAppliedMutation.isPending || application.status === "applied"}
                      onClick={() => markAppliedMutation.mutate(application.id)}
                      variant="secondary"
                    >
                      Mark applied
                    </Button>
                    <Button disabled={resetReadyMutation.isPending} onClick={() => resetReadyMutation.mutate(application.id)} variant="secondary">
                      Reset ready
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No tracked applications yet"
            description="Prepare an application from a job detail page to populate the control center."
            ctaHref="/jobs"
            ctaLabel="Browse jobs"
          />
        )}
      </section>
    </ProtectedPage>
  );
}
