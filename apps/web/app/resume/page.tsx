"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { api } from "@/lib/api";
import type { ResumeTheme } from "@/lib/types";
import { stringifyJson } from "@/lib/utils";
import { useAppStore } from "@/store/app-store";

export default function ResumePage() {
  const pushToast = useAppStore((state) => state.pushToast);
  const [fileId, setFileId] = useState<number | null>(null);
  const [parsedPreview, setParsedPreview] = useState<string>("");
  const [selectedTheme, setSelectedTheme] = useState<string>("classic-ats-light");
  const themesQuery = useQuery({ queryKey: ["resume-themes"], queryFn: () => api<ResumeTheme[]>("/resume-themes") });

  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => api<{ file_id: number }>("/profile/upload-resume", { method: "POST", body: formData }),
    onSuccess: (result) => {
      setFileId(result.file_id);
      pushToast({ title: "Resume uploaded", tone: "success" });
    },
    onError: () => pushToast({ title: "Upload failed", tone: "error" }),
  });

  const parseMutation = useMutation({
    mutationFn: async (id: number) => api<{ parsed: unknown }>(`/profile/parse-resume?file_id=${id}`, { method: "POST" }),
    onSuccess: (result) => {
      setParsedPreview(stringifyJson(result.parsed));
      pushToast({ title: "Resume parsed into your profile", tone: "success" });
    },
    onError: () => pushToast({ title: "Resume parsing failed", tone: "error" }),
  });

  const themeMutation = useMutation({
    mutationFn: async (themeSlug: string) =>
      api("/profile/settings", {
        method: "PUT",
        body: JSON.stringify({
          values: {
            resume_preferences: {
              default_theme: themeSlug,
              ats_mode: true,
            },
          },
        }),
      }),
    onSuccess: () => pushToast({ title: "Default resume theme saved", tone: "success" }),
  });

  const themes = themesQuery.data || [];

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Resume Brain"
          title="Upload and parse your source resume"
          description="Extract structured sections into a fact-locked master profile before tailoring to specific jobs."
        />
        <div className="grid gap-4 xl:grid-cols-[0.85fr_1.15fr]">
          <Card className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Source document</h2>
            <input
              className="block w-full text-sm text-slate-300"
              type="file"
              onChange={async (event) => {
                const file = event.target.files?.[0];
                if (!file) {
                  return;
                }
                const formData = new FormData();
                formData.append("file", file);
                uploadMutation.mutate(formData);
              }}
            />
            <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-300">
              {fileId ? `Uploaded file ID ${fileId}. Ready for parsing.` : "Upload a PDF or DOCX resume to begin."}
            </div>
            <Button disabled={!fileId || parseMutation.isPending} onClick={() => fileId && parseMutation.mutate(fileId)}>
              {parseMutation.isPending ? "Parsing…" : "Parse into profile"}
            </Button>
          </Card>

          <Card className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Parsed preview</h2>
            <pre className="min-h-[360px] overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
              {parsedPreview || "Parsed sections will appear here after extraction."}
            </pre>
          </Card>
        </div>

        <Card className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold text-white">Light ATS themes</h2>
              <p className="text-sm text-slate-400">RenderCV-inspired structured themes for readable, extractable exports.</p>
            </div>
            <Button disabled={themeMutation.isPending} onClick={() => themeMutation.mutate(selectedTheme)} variant="secondary">
              {themeMutation.isPending ? "Saving…" : "Save default theme"}
            </Button>
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            {themes.map((theme) => (
              <button
                key={theme.id}
                className={`rounded-[1.75rem] border p-5 text-left transition ${
                  selectedTheme === theme.slug
                    ? "border-cyan-300/60 bg-cyan-400/10"
                    : "border-white/10 bg-slate-950/60 hover:border-cyan-300/30"
                }`}
                onClick={() => setSelectedTheme(theme.slug)}
                type="button"
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white">{theme.label}</h3>
                    <p className="text-sm text-slate-400">{theme.description}</p>
                  </div>
                  {theme.is_ats_safe ? <Badge tone="success">ATS safe</Badge> : <Badge>Decorative</Badge>}
                </div>
                <div className="mt-4 rounded-2xl border border-white/10 bg-white/95 p-4 text-slate-900">
                  <p className="text-base font-semibold">Alex Builder</p>
                  <p className="text-xs uppercase tracking-[0.22em]" style={{ color: theme.accent_color }}>
                    {theme.label}
                  </p>
                  <div className="mt-3 space-y-2 text-xs">
                    <p>Summary</p>
                    <div className="h-2 rounded bg-slate-300" />
                    <p>Skills</p>
                    <div className="h-2 rounded bg-slate-300" />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </Card>
      </section>
    </ProtectedPage>
  );
}
