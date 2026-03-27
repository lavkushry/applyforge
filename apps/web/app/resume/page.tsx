"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { api } from "@/lib/api";
import { stringifyJson } from "@/lib/utils";
import { useAppStore } from "@/store/app-store";

export default function ResumePage() {
  const pushToast = useAppStore((state) => state.pushToast);
  const [fileId, setFileId] = useState<number | null>(null);
  const [parsedPreview, setParsedPreview] = useState<string>("");

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
      </section>
    </ProtectedPage>
  );
}
