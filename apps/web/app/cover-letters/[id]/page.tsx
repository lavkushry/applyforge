"use client";

import { useMutation } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import type { CoverLetter } from "@/lib/types";

export default function CoverLetterPage() {
  const { id } = useParams<{ id: string }>();
  const [draft, setDraft] = useState("");
  const mutation = useMutation({
    mutationFn: () => api<CoverLetter>(`/jobs/${id}/cover-letter`, { method: "POST" }),
    onSuccess: (result) => setDraft(result.content),
  });

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Cover Letter"
          title="Generate a concise role-specific cover note"
          description="Use the generated draft as a starting point, then refine tone and specifics before submission."
        />
        <Card className="space-y-4">
          <div className="flex justify-between">
            <Button onClick={() => mutation.mutate()}>{mutation.isPending ? "Generating…" : "Generate draft"}</Button>
          </div>
          <Textarea className="min-h-[420px]" value={draft} onChange={(event) => setDraft(event.target.value)} />
        </Card>
      </section>
    </ProtectedPage>
  );
}
