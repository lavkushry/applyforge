"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { ApplicationPrepareResponse, ApplicationRun, CoverLetter, Job, JobScore, ResumeVersion } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const session = useSession();
  const pushToast = useAppStore((state) => state.pushToast);
  const jobQuery = useQuery({
    queryKey: ["job", id],
    queryFn: () => api<Job>(`/jobs/${id}`),
    enabled: Boolean(session.user),
  });
  const eligibilityQuery = useQuery({
    queryKey: ["job-eligibility", id],
    queryFn: () => api<Record<string, unknown>>(`/jobs/${id}/eligibility`),
    enabled: Boolean(session.user),
  });

  const scoreMutation = useMutation({
    mutationFn: () => api<JobScore>(`/jobs/${id}/score`, { method: "POST" }),
    onSuccess: () => pushToast({ title: "Job scored", tone: "success" }),
  });
  const tailorMutation = useMutation({
    mutationFn: () => api<ResumeVersion>(`/jobs/${id}/tailor`, { method: "POST", body: JSON.stringify({ ats_mode: true }) }),
    onSuccess: () => pushToast({ title: "Tailored resume generated", tone: "success" }),
  });
  const coverLetterMutation = useMutation({
    mutationFn: () => api<CoverLetter>(`/jobs/${id}/cover-letter`, { method: "POST" }),
    onSuccess: () => pushToast({ title: "Cover letter generated", tone: "success" }),
  });
  const prepareMutation = useMutation({
    mutationFn: () => api<ApplicationPrepareResponse>(`/applications/${id}/prepare`, { method: "POST" }),
    onSuccess: (payload) =>
      pushToast({
        title: payload.packet.ready ? "Application packet ready" : "Application packet needs review",
        tone: payload.packet.ready ? "success" : "info",
      }),
  });
  const assistedRunMutation = useMutation({
    mutationFn: () => api<ApplicationRun>(`/applications/${id}/run-assisted`, { method: "POST" }),
    onSuccess: (run) => {
      pushToast({ title: `Assisted run ${run.status}`, tone: run.status === "queued" ? "success" : "info" });
      router.push(`/runs/${run.id}`);
    },
  });
  const autoRunMutation = useMutation({
    mutationFn: () => api<ApplicationRun>(`/applications/${id}/run-auto`, { method: "POST" }),
    onSuccess: (run) => {
      pushToast({ title: `Auto run ${run.status}`, tone: run.status === "queued" ? "success" : "info" });
      router.push(`/runs/${run.id}`);
    },
  });

  const job = jobQuery.data;
  const packet = prepareMutation.data?.packet;

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Job Detail"
          title={job?.title || "Loading role…"}
          description="Review normalized metadata, then score, tailor, and move the opportunity into an application run."
        />

        {job ? (
          <div className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
            <Card className="space-y-4">
              <div className="flex flex-wrap items-center gap-3">
                <Badge>{job.remote_type}</Badge>
                <Badge tone="warning">{job.seniority || "seniority pending"}</Badge>
                <Badge tone="default">{job.employment_type || "full-time"}</Badge>
              </div>
              <div className="space-y-2">
                <p className="text-lg font-semibold text-white">{job.company}</p>
                <p className="text-sm text-slate-300">{job.location || "Location not provided"}</p>
                <p className="text-sm text-slate-400">{job.salary || "Salary not specified"}</p>
                {job.application_url ? (
                  <a className="text-sm text-cyan-300" href={job.application_url} rel="noreferrer" target="_blank">
                    Open source application
                  </a>
                ) : null}
              </div>
              <div className="space-y-2">
                <h2 className="text-lg font-semibold text-white">Description</h2>
                <p className="whitespace-pre-wrap text-sm text-slate-300">{job.description}</p>
              </div>
            </Card>

            <Card className="space-y-4">
              <h2 className="text-lg font-semibold text-white">Actions</h2>
              <div className="grid gap-3">
                <Button disabled={scoreMutation.isPending} onClick={() => scoreMutation.mutate()}>
                  {scoreMutation.isPending ? "Scoring…" : "Generate fit score"}
                </Button>
                <Button disabled={tailorMutation.isPending} onClick={() => tailorMutation.mutate()} variant="secondary">
                  {tailorMutation.isPending ? "Tailoring…" : "Generate tailored resume"}
                </Button>
                <Button
                  disabled={coverLetterMutation.isPending}
                  onClick={() => coverLetterMutation.mutate()}
                  variant="secondary"
                >
                  {coverLetterMutation.isPending ? "Writing…" : "Generate cover letter"}
                </Button>
                <Button disabled={prepareMutation.isPending} onClick={() => prepareMutation.mutate()} variant="secondary">
                  {prepareMutation.isPending ? "Preparing…" : "Prepare application packet"}
                </Button>
                <Button disabled={assistedRunMutation.isPending} onClick={() => assistedRunMutation.mutate()}>
                  {assistedRunMutation.isPending ? "Queueing…" : "Run assisted apply"}
                </Button>
                <Button disabled={autoRunMutation.isPending} onClick={() => autoRunMutation.mutate()} variant="secondary">
                  {autoRunMutation.isPending ? "Queueing…" : "Run auto apply"}
                </Button>
              </div>

              <div className="flex flex-wrap gap-3 pt-2">
                <Link href={`/scores/${id}`} className="text-sm text-cyan-300">
                  Score detail
                </Link>
                <Link href={`/tailor/${id}`} className="text-sm text-cyan-300">
                  Tailored resume
                </Link>
                <Link href={`/cover-letters/${id}`} className="text-sm text-cyan-300">
                  Cover letter
                </Link>
              </div>

              <div className="space-y-3 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <p className="text-sm text-slate-300">
                  Latest score: <span className="font-medium text-white">{Math.round(job.latest_score || 0)}</span>
                </p>
                <p className="text-sm text-slate-300">
                  Score revision: <span className="font-medium text-white">{job.latest_score_revision}</span>
                </p>
                <p className="text-sm text-slate-300">
                  Eligibility: <span className="font-medium text-white">{String(eligibilityQuery.data?.reason || "Pending")}</span>
                </p>
              </div>

              <div className="space-y-3 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge>{job.enrichment_status}</Badge>
                  <Badge tone="default">Revision {job.enrichment_revision}</Badge>
                </div>
                <p className="text-sm text-slate-300">
                  Extraction confidence:{" "}
                  <span className="font-medium text-white">
                    {typeof job.enrichment_metadata?.extraction_confidence === "number"
                      ? `${Math.round(Number(job.enrichment_metadata.extraction_confidence) * 100)}%`
                      : "Unknown"}
                  </span>
                </p>
                {Array.isArray(job.normalized_description?.must_have_skills) && job.normalized_description.must_have_skills.length ? (
                  <p className="text-sm text-slate-300">
                    Must-have skills:{" "}
                    <span className="font-medium text-white">
                      {job.normalized_description.must_have_skills.join(", ")}
                    </span>
                  </p>
                ) : null}
                {Array.isArray(job.normalized_description?.nice_to_have_skills) && job.normalized_description.nice_to_have_skills.length ? (
                  <p className="text-sm text-slate-300">
                    Nice-to-have skills:{" "}
                    <span className="font-medium text-white">
                      {job.normalized_description.nice_to_have_skills.join(", ")}
                    </span>
                  </p>
                ) : null}
              </div>

              {packet ? (
                <div className="space-y-3 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge tone={packet.ready ? "success" : "warning"}>
                      {packet.ready ? "Packet ready" : "Needs review"}
                    </Badge>
                    <Badge tone={packet.auto_submit_allowed ? "success" : "default"}>
                      {packet.auto_submit_allowed ? "Auto submit allowed" : "Auto submit blocked"}
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-300">
                    Resume file: <span className="font-medium text-white">{packet.resume_file_id || "Missing"}</span>
                  </p>
                  <p className="text-sm text-slate-300">
                    Cover letter: <span className="font-medium text-white">{packet.cover_letter_id || "Not attached"}</span>
                  </p>
                  {packet.blocking_issues.length ? (
                    <p className="text-sm text-amber-200">Blocking issues: {packet.blocking_issues.join(", ")}</p>
                  ) : null}
                  {packet.missing_answers.length ? (
                    <p className="text-sm text-amber-200">Missing answers: {packet.missing_answers.join(", ")}</p>
                  ) : null}
                </div>
              ) : null}

              <div className="space-y-3 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <p className="text-sm font-medium text-white">Detected tags</p>
                <div className="flex flex-wrap gap-2">
                  {job.tags.map((tag) => (
                    <Badge key={tag}>{tag}</Badge>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        ) : (
          <Card>Loading job details…</Card>
        )}
      </section>
    </ProtectedPage>
  );
}
