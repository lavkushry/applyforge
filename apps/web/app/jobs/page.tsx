"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useMemo, useState } from "react";

import { JobCreateForm } from "@/components/forms/job-create-form";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { IngestionRun, Job, JobFeedEvent, TargetRole } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

export default function JobsPage() {
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const session = useSession();
  const queryClient = useQueryClient();
  const pushToast = useAppStore((state) => state.pushToast);
  const rolesQuery = useQuery({ queryKey: ["roles"], queryFn: () => api<TargetRole[]>("/roles"), enabled: Boolean(session.user) });
  const jobsQuery = useQuery({
    queryKey: ["jobs", roleFilter],
    queryFn: () => api<Job[]>(roleFilter ? `/jobs?role_id=${roleFilter}` : "/jobs"),
    enabled: Boolean(session.user),
  });
  const feedQuery = useQuery({
    queryKey: ["jobs-feed", roleFilter],
    queryFn: () => api<JobFeedEvent[]>(roleFilter ? `/jobs/feed?role_id=${roleFilter}` : "/jobs/feed"),
    enabled: Boolean(session.user),
    refetchInterval: 20000,
  });
  const scrapeMutation = useMutation({
    mutationFn: (roleId: number) => api<IngestionRun>(`/roles/${roleId}/scrape-now`, { method: "POST" }),
    onSuccess: (run) => {
      queryClient.invalidateQueries({ queryKey: ["jobs-feed"] });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      pushToast({
        title: run.status === "running" ? "Discovery started, enrichment queued" : "Role scrape completed",
        tone: "success",
      });
    },
    onError: () => pushToast({ title: "Role scrape failed", tone: "error" }),
  });

  const filtered = useMemo(() => {
    const jobs = jobsQuery.data || [];
    const term = search.toLowerCase();
    if (!term) {
      return jobs;
    }
    return jobs.filter(
      (job) =>
        job.title.toLowerCase().includes(term) ||
        job.company.toLowerCase().includes(term) ||
        job.tags.join(" ").toLowerCase().includes(term),
    );
  }, [jobsQuery.data, search]);

  const roles = rolesQuery.data || [];
  const feed = feedQuery.data || [];
  const selectedRole = roles.find((role) => String(role.id) === roleFilter) || null;

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Discovery"
          title="Job pipeline"
          description="Track a live role-based job feed, link scraped jobs back to sources, and move the best matches into tailored application flows."
        />
        <JobCreateForm
          roles={roles}
          onCreated={(job) => {
            queryClient.setQueryData<Job[]>(["jobs", roleFilter], (current) => [job, ...(current || [])]);
          }}
        />

        <Card className="space-y-4">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div className="space-y-1">
              <h2 className="text-xl font-semibold text-white">Live feed</h2>
              <p className="text-sm text-slate-400">Polling every 20 seconds for fresh role-linked activity.</p>
            </div>
            <div className="flex w-full max-w-2xl flex-col gap-3 lg:flex-row">
              <select
                className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100 lg:max-w-xs"
                value={roleFilter}
                onChange={(event) => setRoleFilter(event.target.value)}
                aria-label="Filter by role"
              >
                <option value="">All roles</option>
                {roles.map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.name}
                  </option>
                ))}
              </select>
              <Input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search role, company, or tags" />
              <Button
                disabled={!selectedRole || scrapeMutation.isPending}
                onClick={() => selectedRole && scrapeMutation.mutate(selectedRole.id)}
                variant="secondary"
              >
                {scrapeMutation.isPending ? "Running…" : "Scrape selected role"}
              </Button>
            </div>
          </div>
          {feed.length ? (
            <div className="grid gap-3 xl:grid-cols-2">
              {feed.slice(0, 8).map((event) => (
                <Card key={event.id} className="space-y-3 border-white/5 bg-slate-950/60">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-white">{event.job?.title || "Job update"}</p>
                      <p className="text-sm text-slate-400">{event.role_name || "Unassigned role"}</p>
                    </div>
                    <Badge>{event.event_type}</Badge>
                  </div>
                  <p className="text-sm text-slate-300">{event.job?.company || "Unknown company"}</p>
                  <div className="flex flex-wrap items-center gap-2">
                    {event.job?.application_url ? (
                      <a className="text-sm text-cyan-300" href={event.job.application_url} rel="noreferrer" target="_blank">
                        Source link
                      </a>
                    ) : null}
                    {event.job?.enrichment_status ? <Badge>{event.job.enrichment_status}</Badge> : null}
                    {event.job?.latest_score ? <Badge tone="success">{Math.round(event.job.latest_score)} match</Badge> : null}
                    {event.job?.latest_recommendation ? <Badge>{event.job.latest_recommendation}</Badge> : null}
                  </div>
                  {typeof event.job?.enrichment_metadata?.extraction_confidence === "number" ? (
                    <p className="text-xs text-slate-400">
                      Enrichment confidence {Math.round(Number(event.job.enrichment_metadata.extraction_confidence) * 100)}%
                    </p>
                  ) : null}
                </Card>
              ))}
            </div>
          ) : (
            <EmptyState title="No feed events yet" description="Create a role with a scrape source or add jobs manually." />
          )}
        </Card>

        <Card className="space-y-4">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <h2 className="text-xl font-semibold text-white">Tracked jobs</h2>
            <div className="flex items-center gap-2">
              {selectedRole ? <Badge>{selectedRole.name}</Badge> : <Badge tone="default">All roles</Badge>}
            </div>
          </div>
          {filtered.length ? (
            <div className="grid gap-4 lg:grid-cols-2">
              {filtered.map((job) => (
                <Link key={job.id} href={`/jobs/${job.id}`}>
                  <Card className="h-full space-y-3 transition hover:border-cyan-400/40">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-lg font-semibold text-white">{job.title}</h3>
                        <p className="text-sm text-slate-300">{job.company}</p>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <Badge>{job.remote_type}</Badge>
                        <Badge>{job.enrichment_status}</Badge>
                        {job.latest_score ? <Badge tone="success">{Math.round(job.latest_score)} match</Badge> : null}
                      </div>
                    </div>
                    <p className="text-sm text-slate-400">{job.location || "Location not provided"}</p>
                    <p className="text-sm text-slate-300">{job.description.slice(0, 180)}…</p>
                    {typeof job.enrichment_metadata?.extraction_confidence === "number" ? (
                      <p className="text-xs text-slate-400">
                        Extraction confidence {Math.round(Number(job.enrichment_metadata.extraction_confidence) * 100)}%
                      </p>
                    ) : null}
                    <div className="flex flex-wrap gap-2">
                      {job.tags.slice(0, 4).map((tag) => (
                        <Badge key={tag} tone="default">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          ) : (
            <EmptyState title="No jobs yet" description="Add a job above to start scoring and tailoring." />
          )}
        </Card>
      </section>
    </ProtectedPage>
  );
}
