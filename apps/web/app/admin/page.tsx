"use client";

import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { useSession } from "@/hooks/use-session";
import { api } from "@/lib/api";
import type { HealthStatus } from "@/lib/types";

export default function AdminPage() {
  const session = useSession();
  const enabled = Boolean(session.user);
  const runsQuery = useQuery({
    queryKey: ["admin-runs"],
    queryFn: () => api<Array<Record<string, unknown>>>("/admin/runs"),
    enabled,
  });
  const errorsQuery = useQuery({
    queryKey: ["admin-errors"],
    queryFn: () => api<Array<Record<string, unknown>>>("/admin/errors"),
    enabled,
  });
  const logsQuery = useQuery({
    queryKey: ["prompt-logs"],
    queryFn: () => api<Array<Record<string, unknown>>>("/admin/prompt-logs"),
    enabled,
  });
  const ingestionQuery = useQuery({
    queryKey: ["ingestion-runs"],
    queryFn: () => api<Array<Record<string, unknown>>>("/admin/ingestion-runs"),
    enabled,
  });
  const otpQuery = useQuery({
    queryKey: ["otp-events"],
    queryFn: () => api<Array<Record<string, unknown>>>("/admin/otp-events"),
    enabled,
  });
  const healthQuery = useQuery({ queryKey: ["health"], queryFn: () => api<HealthStatus>("/admin/health"), enabled });

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Diagnostics"
          title="Internal operations panel"
          description="Inspect automation run states, prompt traces, and basic service health before hardening deeper ops flows."
        />

        <div className="grid gap-4 xl:grid-cols-3">
          <Card className="space-y-3">
            <p className="text-sm font-medium text-white">API health</p>
            <Badge tone={healthQuery.data?.status === "ok" ? "success" : "danger"}>{healthQuery.data?.status || "unknown"}</Badge>
            <p className="text-sm text-slate-300">Database: {healthQuery.data?.database || "pending"}</p>
            <p className="text-sm text-slate-300">Redis: {healthQuery.data?.redis || "pending"}</p>
          </Card>
          <Card className="space-y-3">
            <p className="text-sm font-medium text-white">Recent runs</p>
            <p className="text-4xl font-semibold text-white">{runsQuery.data?.length || 0}</p>
          </Card>
          <Card className="space-y-3">
            <p className="text-sm font-medium text-white">Paused or failed steps</p>
            <p className="text-4xl font-semibold text-white">{errorsQuery.data?.length || 0}</p>
          </Card>
        </div>

        <div className="grid gap-4 xl:grid-cols-3">
          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Runs</h2>
            <pre className="overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
              {JSON.stringify(runsQuery.data || [], null, 2)}
            </pre>
          </Card>
          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Errors</h2>
            <pre className="overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
              {JSON.stringify(errorsQuery.data || [], null, 2)}
            </pre>
          </Card>
          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Prompt logs</h2>
            <pre className="overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
              {JSON.stringify(logsQuery.data || [], null, 2)}
            </pre>
          </Card>
        </div>

        <div className="grid gap-4 xl:grid-cols-2">
          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Ingestion runs</h2>
            <pre className="overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
              {JSON.stringify(ingestionQuery.data || [], null, 2)}
            </pre>
          </Card>
          <Card className="space-y-3">
            <h2 className="text-lg font-semibold text-white">OTP events</h2>
            <pre className="overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
              {JSON.stringify(otpQuery.data || [], null, 2)}
            </pre>
          </Card>
        </div>
      </section>
    </ProtectedPage>
  );
}
