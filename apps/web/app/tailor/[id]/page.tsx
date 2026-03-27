"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { api } from "@/lib/api";
import type { ResumeVersion } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

export default function TailorPage() {
  const { id } = useParams<{ id: string }>();
  const pushToast = useAppStore((state) => state.pushToast);
  const mutation = useMutation({
    mutationFn: () => api<ResumeVersion>(`/jobs/${id}/tailor`, { method: "POST" }),
  });

  const exportMutation = useMutation({
    mutationFn: (resumeVersionId: number) =>
      api<{ file_id: number; path: string }>("/files/export-resume-pdf", {
        method: "POST",
        body: JSON.stringify({ resume_version_id: resumeVersionId }),
      }),
    onSuccess: () => pushToast({ title: "PDF exported", tone: "success" }),
  });

  const version = mutation.data;
  const content = version?.content_json as Record<string, unknown> | undefined;

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Resume Tailoring"
          title="Generate and review a job-specific resume"
          description="ApplyForge keeps all tailoring fact-locked and only reorders or emphasizes verified content."
        />

        <Card className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => mutation.mutate()}>{mutation.isPending ? "Generating…" : "Generate tailored resume"}</Button>
            <Button
              disabled={!version || exportMutation.isPending}
              onClick={() => version && exportMutation.mutate(version.id)}
              variant="secondary"
            >
              {exportMutation.isPending ? "Exporting…" : "Export PDF"}
            </Button>
          </div>

          {content ? (
            <div className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
              <Card className="space-y-3 border-white/5 bg-slate-950/60">
                <h2 className="text-lg font-semibold text-white">Preview</h2>
                <p className="text-2xl font-semibold text-white">{(content.basics as Record<string, string>)?.full_name}</p>
                <p className="text-sm text-slate-300">{String(content.summary || "")}</p>
                <div className="space-y-2">
                  <p className="text-sm font-medium text-white">Skills</p>
                  <p className="text-sm text-slate-300">{(content.skills as string[]).join(", ")}</p>
                </div>
              </Card>
              <Card className="space-y-3 border-white/5 bg-slate-950/60">
                <h2 className="text-lg font-semibold text-white">Structured content</h2>
                <pre className="overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
                  {JSON.stringify(content, null, 2)}
                </pre>
              </Card>
            </div>
          ) : (
            <p className="text-sm text-slate-300">Generate a tailored version to preview and export it.</p>
          )}
        </Card>
      </section>
    </ProtectedPage>
  );
}
