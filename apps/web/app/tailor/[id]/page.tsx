"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { api } from "@/lib/api";
import type { ResumePreview, ResumeTheme, ResumeVersion, TargetRole } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

export default function TailorPage() {
  const { id } = useParams<{ id: string }>();
  const pushToast = useAppStore((state) => state.pushToast);
  const [roleId, setRoleId] = useState("");
  const [themeId, setThemeId] = useState("");
  const rolesQuery = useQuery({ queryKey: ["roles"], queryFn: () => api<TargetRole[]>("/roles") });
  const themesQuery = useQuery({ queryKey: ["resume-themes"], queryFn: () => api<ResumeTheme[]>("/resume-themes") });
  const mutation = useMutation({
    mutationFn: () =>
      api<ResumeVersion>(`/jobs/${id}/tailor`, {
        method: "POST",
        body: JSON.stringify({
          role_id: roleId ? Number(roleId) : null,
          theme_id: themeId ? Number(themeId) : null,
          ats_mode: true,
        }),
      }),
  });
  const previewQuery = useQuery({
    queryKey: ["resume-preview", mutation.data?.id, themeId],
    queryFn: () =>
      api<ResumePreview>(
        `/resume-versions/${mutation.data?.id}/preview${themeId ? `?theme_id=${themeId}` : ""}`,
        { method: "POST" },
      ),
    enabled: Boolean(mutation.data?.id),
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
  const preview = previewQuery.data;
  const roles = rolesQuery.data || [];
  const themes = themesQuery.data || [];

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Resume Tailoring"
          title="Generate and review a job-specific resume"
          description="ApplyForge keeps all tailoring fact-locked and only reorders or emphasizes verified content."
        />

        <Card className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Role strategy</label>
              <select
                className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
                value={roleId}
                onChange={(event) => setRoleId(event.target.value)}
              >
                <option value="">Use job-linked role</option>
                {roles.map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Resume theme</label>
              <select
                className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
                value={themeId}
                onChange={(event) => setThemeId(event.target.value)}
              >
                <option value="">Default ATS theme</option>
                {themes.map((theme) => (
                  <option key={theme.id} value={theme.id}>
                    {theme.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
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
                {version ? (
                  <div className="flex flex-wrap gap-2">
                    <Badge>{version.theme_variant}</Badge>
                    <Badge tone="success">{version.export_status}</Badge>
                  </div>
                ) : null}
                <p className="text-2xl font-semibold text-white">{(content.basics as Record<string, string>)?.full_name}</p>
                <p className="text-sm text-slate-300">{String(content.summary || "")}</p>
                <div className="space-y-2">
                  <p className="text-sm font-medium text-white">Skills</p>
                  <p className="text-sm text-slate-300">{(content.skills as string[]).join(", ")}</p>
                </div>
                {preview ? (
                  <div className="space-y-2 rounded-2xl border border-white/10 bg-slate-950/80 p-4">
                    <p className="text-sm font-medium text-white">{preview.theme.label}</p>
                    {preview.blocks.map((block) => (
                      <div key={block.title} className="space-y-1">
                        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{block.title}</p>
                        {block.lines.map((line) => (
                          <p key={line} className="text-sm text-slate-300">
                            {line}
                          </p>
                        ))}
                      </div>
                    ))}
                  </div>
                ) : null}
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
