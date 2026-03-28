"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { api } from "@/lib/api";
import type { ResumeTemplateCatalog, ResumeTemplateRender, ResumeTheme } from "@/lib/types";
import { stringifyJson } from "@/lib/utils";
import { useAppStore } from "@/store/app-store";

export default function ResumePage() {
  const pushToast = useAppStore((state) => state.pushToast);
  const [fileId, setFileId] = useState<number | null>(null);
  const [parsedPreview, setParsedPreview] = useState<string>("");
  const [selectedTheme, setSelectedTheme] = useState<string>("classic-ats-light");
  const [selectedTemplateKey, setSelectedTemplateKey] = useState<string>("");
  const [renderedTemplatePreview, setRenderedTemplatePreview] = useState<string>("");
  const themesQuery = useQuery({ queryKey: ["resume-themes"], queryFn: () => api<ResumeTheme[]>("/resume-themes") });
  const templateCatalogQuery = useQuery({
    queryKey: ["resume-templates"],
    queryFn: () => api<ResumeTemplateCatalog>("/resume/templates"),
  });

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

  const templateRenderMutation = useMutation({
    mutationFn: async (templateKey: string) =>
      api<ResumeTemplateRender>("/resume/templates/render", {
        method: "POST",
        body: JSON.stringify({ template_key: templateKey }),
      }),
    onSuccess: (result) => {
      setRenderedTemplatePreview(result.rendered_content);
      pushToast({ title: `${result.template.label} rendered from your current profile`, tone: "success" });
    },
    onError: () => pushToast({ title: "Could not render the starter template from your profile", tone: "error" }),
  });

  const themes = themesQuery.data || [];
  const templateCatalog = templateCatalogQuery.data;
  const selectedTemplate = templateCatalog?.templates.find((template) => template.key === selectedTemplateKey) ?? null;
  const selectedTemplateSections =
    templateCatalog?.sections.filter((section) => selectedTemplate?.section_keys.includes(section.key)) ?? [];

  useEffect(() => {
    if (!selectedTemplateKey && templateCatalog?.templates.length) {
      setSelectedTemplateKey(templateCatalog.templates[0].key);
    }
  }, [selectedTemplateKey, templateCatalog]);

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

        <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
          <Card className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold text-white">Structured starter templates</h2>
                <p className="text-sm text-slate-400">
                  ResumeCraftr-style source templates for Markdown and LaTeX inspection, editing, and export workflows.
                </p>
              </div>
              <Button
                disabled={!selectedTemplateKey || templateRenderMutation.isPending}
                onClick={() => selectedTemplateKey && templateRenderMutation.mutate(selectedTemplateKey)}
                variant="secondary"
              >
                {templateRenderMutation.isPending ? "Rendering…" : "Render from current profile"}
              </Button>
            </div>
            <div className="grid gap-3">
              {templateCatalog?.templates.map((template) => (
                <button
                  key={template.key}
                  className={`rounded-[1.5rem] border p-4 text-left transition ${
                    selectedTemplateKey === template.key
                      ? "border-cyan-300/60 bg-cyan-400/10"
                      : "border-white/10 bg-slate-950/60 hover:border-cyan-300/30"
                  }`}
                  onClick={() => setSelectedTemplateKey(template.key)}
                  type="button"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-base font-semibold text-white">{template.label}</h3>
                      <p className="mt-1 text-sm text-slate-400">{template.description}</p>
                    </div>
                    <Badge>{template.format.toUpperCase()}</Badge>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {template.section_keys.map((key) => (
                      <Badge key={key}>
                        {key}
                      </Badge>
                    ))}
                  </div>
                </button>
              ))}
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
              <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Selected template</h3>
              <p className="mt-2 text-base font-semibold text-white">{selectedTemplate?.label || "Choose a template"}</p>
              <div className="mt-3 space-y-2 text-sm text-slate-300">
                {selectedTemplateSections.map((section) => (
                  <div key={section.key}>
                    <p className="font-medium text-white">{section.label}</p>
                    <p className="text-slate-400">{section.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Rendered source preview</h2>
            <pre className="min-h-[420px] overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs text-slate-300">
              {renderedTemplatePreview ||
                "Render a starter template from your current canonical profile to inspect the Markdown or LaTeX source."}
            </pre>
          </Card>
        </div>
      </section>
    </ProtectedPage>
  );
}
