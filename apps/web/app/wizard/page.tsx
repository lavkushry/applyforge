"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Route } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { StatCard } from "@/components/ui/stat-card";
import { api } from "@/lib/api";
import type { TargetRole, WizardSummary } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

export default function WizardPage() {
  const queryClient = useQueryClient();
  const pushToast = useAppStore((state) => state.pushToast);
  const wizardQuery = useQuery({
    queryKey: ["setup-wizard"],
    queryFn: () => api<WizardSummary>("/setup/wizard"),
  });

  const bootstrapMutation = useMutation({
    mutationFn: (templateKey: string) =>
      api<TargetRole>("/setup/wizard/bootstrap-role", {
        method: "POST",
        body: JSON.stringify({ template_key: templateKey }),
      }),
    onSuccess: (role) => {
      queryClient.invalidateQueries({ queryKey: ["roles"] });
      queryClient.invalidateQueries({ queryKey: ["setup-wizard"] });
      pushToast({ title: `Bootstrapped ${role.name}`, tone: "success" });
    },
    onError: () => pushToast({ title: "Could not bootstrap role", tone: "error" }),
  });

  const wizard = wizardQuery.data;

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Setup Wizard"
          title="Get ApplyForge operational"
          description="This is the ApplyPilot-style bootstrap pass: set up profile facts, resume input, role strategy, and inbox readiness before you turn on automation."
        />

        <div className="grid gap-4 lg:grid-cols-4">
          <StatCard label="Roles" value={String(wizard?.role_count || 0)} hint="Target role strategies currently configured." />
          <StatCard label="Jobs" value={String(wizard?.job_count || 0)} hint="Active discovered jobs in the local feed." />
          <StatCard label="Tailored docs" value={String(wizard?.tailored_resume_count || 0)} hint="Resume versions generated for specific jobs." />
          <StatCard
            label="Inbox"
            value={wizard?.inbox_ready ? "Ready" : "Optional"}
            hint="Connect inbox access if you want OTP lookup during application runs."
          />
        </div>

        <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
          <Card className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Readiness</h2>
            <div className="space-y-3">
              {wizard?.steps.map((step) => (
                <div key={step.key} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <h3 className="text-base font-semibold text-white">{step.title}</h3>
                      <p className="mt-1 text-sm text-slate-300">{step.description}</p>
                    </div>
                    <Badge tone={step.status === "complete" ? "success" : step.status === "optional" ? "default" : "warning"}>
                      {step.status}
                    </Badge>
                  </div>
                  <div className="mt-3">
                    <Link href={step.href as Route}>
                      <Button variant="secondary">Open</Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Recommended search templates</h2>
            <p className="text-sm text-slate-300">
              These packaged templates mirror the kind of search bootstrap ApplyPilot ships, but they create ApplyForge role strategies and source presets instead of CLI config files.
            </p>
            <div className="space-y-4">
              {wizard?.recommended_templates.map((template) => (
                <div key={template.key} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h3 className="text-base font-semibold text-white">{template.label}</h3>
                      <p className="text-sm text-slate-300">{template.role_name}</p>
                    </div>
                    <Button
                      disabled={bootstrapMutation.isPending}
                      onClick={() => bootstrapMutation.mutate(template.key)}
                      variant="secondary"
                    >
                      {bootstrapMutation.isPending ? "Creating…" : "Bootstrap role"}
                    </Button>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {template.keywords.map((keyword) => (
                      <Badge key={keyword}>{keyword}</Badge>
                    ))}
                  </div>
                  <p className="mt-3 text-sm text-slate-400">
                    Preferred locations: {template.preferred_locations.join(", ") || "Any"} · Sources:{" "}
                    {template.source_preset_keys.join(", ") || "Manual only"}
                  </p>
                </div>
              ))}
            </div>
            {wizard?.blocked_domains.length ? (
              <div className="rounded-2xl border border-amber-400/20 bg-amber-500/10 p-4 text-sm text-amber-100">
                Reference blocked domains from the packaged registry: {wizard.blocked_domains.join(", ")}
              </div>
            ) : null}
          </Card>
        </div>
      </section>
    </ProtectedPage>
  );
}
