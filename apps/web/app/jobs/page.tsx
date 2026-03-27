"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useMemo, useState } from "react";

import { JobCreateForm } from "@/components/forms/job-create-form";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { Job } from "@/lib/types";

export default function JobsPage() {
  const [search, setSearch] = useState("");
  const session = useSession();
  const queryClient = useQueryClient();
  const jobsQuery = useQuery({ queryKey: ["jobs"], queryFn: () => api<Job[]>("/jobs"), enabled: Boolean(session.user) });

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

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Discovery"
          title="Job pipeline"
          description="Import opportunities, keep them normalized, and move the best matches into tailored application flows."
        />
        <JobCreateForm
          onCreated={(job) => {
            queryClient.setQueryData<Job[]>(["jobs"], (current) => [job, ...(current || [])]);
          }}
        />

        <Card className="space-y-4">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <h2 className="text-xl font-semibold text-white">Tracked jobs</h2>
            <div className="w-full max-w-sm">
              <Input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search role, company, or tags" />
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
                      <Badge>{job.remote_type}</Badge>
                    </div>
                    <p className="text-sm text-slate-400">{job.location || "Location not provided"}</p>
                    <p className="text-sm text-slate-300">{job.description.slice(0, 180)}…</p>
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
