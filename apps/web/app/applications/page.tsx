"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { Application } from "@/lib/types";

const statuses = ["discovered", "ready_to_apply", "applied", "interview", "offer"] as const;

export default function ApplicationsPage() {
  const session = useSession();
  const applicationsQuery = useQuery({
    queryKey: ["applications"],
    queryFn: () => api<Application[]>("/applications"),
    enabled: Boolean(session.user),
  });
  const applications = applicationsQuery.data || [];

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Tracker"
          title="Applications board"
          description="Track jobs from discovery through interviews with linked automation runs and diagnostics."
        />

        {applications.length ? (
          <div className="grid gap-4 xl:grid-cols-5">
            {statuses.map((status) => (
              <Card key={status} className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">{status}</h2>
                  <Badge>{applications.filter((application) => application.status === status).length}</Badge>
                </div>
                <div className="space-y-3">
                  {applications
                    .filter((application) => application.status === status)
                    .map((application) => (
                      <Link
                        key={application.id}
                        href={application.latest_run_id ? `/runs/${application.latest_run_id}` : `/jobs/${application.job_id}`}
                        className="block rounded-2xl border border-white/10 bg-slate-950/70 p-4"
                      >
                        <p className="font-medium text-white">{application.job?.title || `Job #${application.job_id}`}</p>
                        <p className="text-sm text-slate-400">{application.job?.company || "Unknown company"}</p>
                      </Link>
                    ))}
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No tracked applications yet"
            description="Prepare an application from a job detail page to populate the tracker board."
            ctaHref="/jobs"
            ctaLabel="Browse jobs"
          />
        )}
      </section>
    </ProtectedPage>
  );
}
