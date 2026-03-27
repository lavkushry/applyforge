"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { CoverLetter, Job, JobScore, ResumeVersion } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const session = useSession();
  const pushToast = useAppStore((state) => state.pushToast);
  const jobQuery = useQuery({
    queryKey: ["job", id],
    queryFn: () => api<Job>(`/jobs/${id}`),
    enabled: Boolean(session.user),
  });

  const scoreMutation = useMutation({
    mutationFn: () => api<JobScore>(`/jobs/${id}/score`, { method: "POST" }),
    onSuccess: () => pushToast({ title: "Job scored", tone: "success" }),
  });
  const tailorMutation = useMutation({
    mutationFn: () => api<ResumeVersion>(`/jobs/${id}/tailor`, { method: "POST" }),
    onSuccess: () => pushToast({ title: "Tailored resume generated", tone: "success" }),
  });
  const coverLetterMutation = useMutation({
    mutationFn: () => api<CoverLetter>(`/jobs/${id}/cover-letter`, { method: "POST" }),
    onSuccess: () => pushToast({ title: "Cover letter generated", tone: "success" }),
  });

  const job = jobQuery.data;

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
