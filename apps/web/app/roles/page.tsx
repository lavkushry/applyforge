"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { RoleCreateForm } from "@/components/forms/role-create-form";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { api } from "@/lib/api";
import type { IngestionRun, TargetRole } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

export default function RolesPage() {
  const pushToast = useAppStore((state) => state.pushToast);
  const queryClient = useQueryClient();
  const rolesQuery = useQuery({ queryKey: ["roles"], queryFn: () => api<TargetRole[]>("/roles") });
  const runsQuery = useQuery({ queryKey: ["ingestion-runs"], queryFn: () => api<IngestionRun[]>("/roles/ingestion-runs") });

  const scrapeMutation = useMutation({
    mutationFn: (roleId: number) => api<IngestionRun>(`/roles/${roleId}/scrape-now`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs-feed"] });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["ingestion-runs"] });
      pushToast({ title: "Scrape run completed", tone: "success" });
    },
    onError: () => pushToast({ title: "Scrape run failed", tone: "error" }),
  });

  const roles = rolesQuery.data || [];
  const runs = runsQuery.data || [];

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Role Strategies"
          title="Define what ApplyForge should hunt for"
          description="Each role strategy drives scraping, scoring, tailoring thresholds, and automation eligibility."
        />

        <RoleCreateForm />

        <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
          <Card className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Active roles</h2>
            {roles.length ? (
              <div className="space-y-3">
                {roles.map((role) => (
                  <Card key={role.id} className="space-y-3 border-white/5 bg-slate-950/60">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <h3 className="text-lg font-semibold text-white">{role.name}</h3>
                        <p className="text-sm text-slate-300">{role.keywords.join(", ") || "No keywords"}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge tone={role.automation_enabled ? "success" : "default"}>
                          {role.automation_enabled ? "Automation on" : "Manual review"}
                        </Badge>
                        <Button
                          variant="secondary"
                          disabled={scrapeMutation.isPending}
                          onClick={() => scrapeMutation.mutate(role.id)}
                        >
                          {scrapeMutation.isPending ? "Running…" : "Scrape now"}
                        </Button>
                      </div>
                    </div>
                    <p className="text-sm text-slate-400">
                      Remote: {role.remote_preference} · Min auto score: {role.min_auto_apply_score} · Cadence:{" "}
                      {role.scrape_cadence_minutes}m
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {role.sources.length ? role.sources.map((source) => (
                        <Badge key={source.id}>{source.kind}</Badge>
                      )) : <Badge tone="default">Manual import only</Badge>}
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState title="No role strategies yet" description="Create a role to drive scraping and automation." />
            )}
          </Card>

          <Card className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Recent scrape runs</h2>
            {runs.length ? (
              <div className="space-y-3">
                {runs.slice(0, 8).map((run) => (
                  <div key={run.id} className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-medium text-white">Role #{run.role_id}</p>
                      <Badge>{run.status}</Badge>
                    </div>
                    <p className="text-sm text-slate-400">
                      {run.discovered_count} discovered · {run.inserted_count} inserted · {run.updated_count} updated
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No scrape runs yet" description="Run your first scrape from a role strategy." />
            )}
          </Card>
        </div>
      </section>
    </ProtectedPage>
  );
}
