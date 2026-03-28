"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { ProtectedPage } from "@/components/ui/protected-page";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { Application, CandidateProfile, Job, JobFeedEvent, TargetRole } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const session = useSession();
  const jobsQuery = useQuery({ queryKey: ["jobs"], queryFn: () => api<Job[]>("/jobs"), enabled: Boolean(session.user) });
  const applicationsQuery = useQuery({
    queryKey: ["applications"],
    queryFn: () => api<Application[]>("/applications"),
    enabled: Boolean(session.user),
  });
  const rolesQuery = useQuery({ queryKey: ["roles"], queryFn: () => api<TargetRole[]>("/roles"), enabled: Boolean(session.user) });
  const feedQuery = useQuery({ queryKey: ["jobs-feed"], queryFn: () => api<JobFeedEvent[]>("/jobs/feed"), enabled: Boolean(session.user) });
  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      try {
        return await api<CandidateProfile>("/profile");
      } catch {
        return null;
      }
    },
    retry: false,
    enabled: Boolean(session.user),
  });

  const jobs = jobsQuery.data || [];
  const applications = applicationsQuery.data || [];
  const roles = rolesQuery.data || [];
  const feed = feedQuery.data || [];

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Workspace"
          title="Job hunt command center"
          description="Track pipeline health, fill profile gaps, and move your highest-fit jobs into tailored and application-ready states."
        />

        <div className="grid gap-4 lg:grid-cols-3">
          <StatCard label="Jobs tracked" value={String(jobs.length)} hint="Normalized opportunities across your active search." />
          <StatCard
            label="Role strategies"
            value={String(roles.length)}
            hint="Each role drives scraping, scoring thresholds, and automation policy."
          />
          <StatCard
            label="Profile status"
            value={profileQuery.data ? "Ready" : "Needs setup"}
            hint="A fact-locked profile unlocks safer tailoring and auto-fill answers."
          />
        </div>

        <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
          <Card className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">Latest jobs</h2>
              <Link href="/jobs" className="text-sm text-cyan-300">
                View all
              </Link>
            </div>
            {jobs.length ? (
              <div className="space-y-3">
                {jobs.slice(0, 5).map((job) => (
                  <Link
                    key={job.id}
                    href={`/jobs/${job.id}`}
                    className="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3"
                  >
                    <div>
                      <p className="font-medium text-white">{job.title}</p>
                      <p className="text-sm text-slate-400">
                        {job.company} · {job.location || "Location not set"}
                      </p>
                    </div>
                    <p className="text-xs text-slate-500">{formatDate(job.created_at)}</p>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState
                title="No jobs imported yet"
                description="Add your first job description to start scoring and tailoring."
                ctaHref="/jobs"
                ctaLabel="Add jobs"
              />
            )}
          </Card>

          <Card className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Immediate next steps</h2>
            <div className="space-y-3">
              {[
                profileQuery.data
                  ? "Profile is loaded. Parse a fresher resume if your experience has changed."
                  : "Upload a resume and create your canonical candidate profile.",
                roles.length ? `You have ${roles.length} role strategies. Run a scrape to refresh the feed.` : "Create your first role strategy before running a scrape.",
                feed.length ? `Feed has ${feed.length} recent events. Review fresh matches from the jobs page.` : "No feed activity yet. Attach a scrape source to a role.",
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
                  {item}
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <StatCard label="Applications" value={String(applications.length)} hint="Runs, statuses, and review checkpoints captured in one board." />
          <StatCard label="Feed events" value={String(feed.length)} hint="Recent discoveries and updates across your active role strategies." />
        </div>
      </section>
    </ProtectedPage>
  );
}
