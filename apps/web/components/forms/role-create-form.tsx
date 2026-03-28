"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import type { DiscoveryPresetCatalog, TargetRole } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

const schema = z.object({
  name: z.string().min(2),
  keywords: z.string().default("python, fastapi, react, typescript"),
  preferred_locations: z.string().default("remote, india"),
  source_kind: z.enum(["manual", "greenhouse_board", "lever_board", "workday_board", "direct_url"]).default("manual"),
  source_label: z.string().default(""),
  source_url: z.string().url().or(z.literal("")).default(""),
  source_preset_key: z.string().default(""),
});

type FormValues = z.infer<typeof schema>;

export function RoleCreateForm() {
  const pushToast = useAppStore((state) => state.pushToast);
  const queryClient = useQueryClient();
  const presetsQuery = useQuery({
    queryKey: ["role-source-presets"],
    queryFn: () => api<DiscoveryPresetCatalog>("/roles/source-presets"),
  });
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "Senior Full Stack Engineer",
      keywords: "python, fastapi, react, typescript, ai",
      preferred_locations: "remote, india",
      source_kind: "manual",
      source_label: "",
      source_url: "",
      source_preset_key: "",
    },
  });

  const sourcePresetKey = form.watch("source_preset_key");
  const selectedPreset = presetsQuery.data?.source_presets.find((preset) => preset.key === sourcePresetKey);

  const mutation = useMutation({
    mutationFn: async (values: FormValues) =>
      api<TargetRole>("/roles", {
        method: "POST",
        body: JSON.stringify({
          name: values.name,
          aliases: [],
          keywords: values.keywords.split(",").map((value) => value.trim()).filter(Boolean),
          preferred_locations: values.preferred_locations.split(",").map((value) => value.trim()).filter(Boolean),
          remote_preference: "remote",
          salary_target: "",
          visa_preference: "unknown",
          seniority: "senior",
          companies_include: [],
          companies_exclude: [],
          scrape_cadence_minutes: 30,
          automation_enabled: true,
          min_auto_apply_score: 85,
          active: true,
          sources:
            ((selectedPreset?.kind || values.source_kind) !== "manual" && (selectedPreset?.base_url || values.source_url))
              ? [
                  {
                    kind: selectedPreset?.kind || values.source_kind,
                    label: selectedPreset?.label || values.source_label,
                    base_url: selectedPreset?.base_url || values.source_url,
                    config: selectedPreset?.config || {},
                    enabled: true,
                  },
                ]
              : [],
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles"] });
      pushToast({ title: "Role strategy saved", tone: "success" });
      form.reset();
    },
    onError: () => pushToast({ title: "Failed to save role", tone: "error" }),
  });

  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <CardTitle>Create a role strategy</CardTitle>
        <CardDescription>Define which role you want to target and optionally attach a scrape source.</CardDescription>
      </div>
      <form className="grid gap-4 lg:grid-cols-2" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Role name</label>
          <Input {...form.register("name")} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Keywords</label>
          <Input {...form.register("keywords")} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Preferred locations</label>
          <Input {...form.register("preferred_locations")} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Source kind</label>
          <select
            className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
            {...form.register("source_kind")}
            disabled={Boolean(selectedPreset)}
          >
            <option value="manual">Manual only</option>
            <option value="greenhouse_board">Greenhouse board</option>
            <option value="lever_board">Lever board</option>
            <option value="workday_board">Workday board</option>
            <option value="direct_url">Direct careers URL</option>
          </select>
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Preset source</label>
          <select
            className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
            {...form.register("source_preset_key")}
          >
            <option value="">Custom or manual</option>
            {presetsQuery.data?.source_presets.map((preset) => (
              <option key={preset.key} value={preset.key}>
                {preset.label} · {preset.kind}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Source label</label>
          <Input {...form.register("source_label")} placeholder="Nimbus AI Careers" disabled={Boolean(selectedPreset)} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Source URL</label>
          <Input
            {...form.register("source_url")}
            placeholder="https://boards.greenhouse.io/example"
            disabled={Boolean(selectedPreset)}
          />
        </div>
        {selectedPreset ? (
          <div className="lg:col-span-2 rounded-2xl border border-cyan-400/20 bg-cyan-500/10 p-4 text-sm text-cyan-50">
            Using preset <span className="font-semibold">{selectedPreset.label}</span>. The source kind, URL, and config will be attached automatically.
          </div>
        ) : null}
        <div className="lg:col-span-2">
          <Button disabled={mutation.isPending} type="submit">
            {mutation.isPending ? "Saving…" : "Save role strategy"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
