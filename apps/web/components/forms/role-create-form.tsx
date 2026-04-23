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
  source_kind: z.enum(["manual", "greenhouse_board", "lever_board", "workday_board", "direct_url", "jobspy_search"]).default("manual"),
  source_label: z.string().default(""),
  source_url: z.string().url().or(z.literal("")).default(""),
  source_preset_key: z.string().default(""),
  jobspy_sites: z.string().default("linkedin, indeed, glassdoor, google"),
  jobspy_location: z.string().default(""),
  jobspy_country_indeed: z.string().default(""),
  jobspy_results_wanted: z.coerce.number().int().min(1).max(200).default(25),
  jobspy_hours_old: z.coerce.number().int().min(1).max(720).default(168),
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
      jobspy_sites: "linkedin, indeed, glassdoor, google",
      jobspy_location: "",
      jobspy_country_indeed: "",
      jobspy_results_wanted: 25,
      jobspy_hours_old: 168,
    },
  });

  const selectedSourceKind = form.watch("source_kind");
  const sourcePresetKey = form.watch("source_preset_key");
  const selectedPreset = presetsQuery.data?.source_presets.find((preset) => preset.key === sourcePresetKey);
  const resolvedSourceKind = selectedPreset?.kind || selectedSourceKind;
  const isJobSpySource = resolvedSourceKind === "jobspy_search";

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const resolvedKind = selectedPreset?.kind || values.source_kind;
      const customJobSpySites = values.jobspy_sites
        .split(",")
        .map((value) => value.trim().toLowerCase().replaceAll("-", "_"))
        .filter(Boolean);
      const jobSpyConfig = {
        site_names: customJobSpySites.length ? customJobSpySites : ["linkedin", "indeed", "glassdoor", "google"],
        ...(values.jobspy_location.trim() ? { location: values.jobspy_location.trim() } : {}),
        ...(values.jobspy_country_indeed.trim() ? { country_indeed: values.jobspy_country_indeed.trim() } : {}),
        results_wanted: values.jobspy_results_wanted,
        hours_old: values.jobspy_hours_old,
        linkedin_fetch_description: true,
      };
      const sourceConfig = selectedPreset?.config || (resolvedKind === "jobspy_search" ? jobSpyConfig : {});
      const sourceLabel =
        selectedPreset?.label || values.source_label || (resolvedKind === "jobspy_search" ? "JobSpy multi-board search" : "");
      const sourceBaseUrl = selectedPreset?.base_url || (resolvedKind === "jobspy_search" ? "" : values.source_url);
      return api<TargetRole>("/roles", {
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
            (resolvedKind !== "manual" && (sourceBaseUrl || resolvedKind === "jobspy_search"))
              ? [
                  {
                    kind: resolvedKind,
                    label: sourceLabel,
                    base_url: sourceBaseUrl,
                    config: sourceConfig,
                    enabled: true,
                  },
                ]
              : [],
        }),
      });
    },
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
          <label htmlFor="name" className="text-sm text-slate-300">Role name</label>
          <Input id="name" {...form.register("name")} />
        </div>
        <div className="space-y-2">
          <label htmlFor="keywords" className="text-sm text-slate-300">Keywords</label>
          <Input id="keywords" {...form.register("keywords")} />
        </div>
        <div className="space-y-2">
          <label htmlFor="preferred_locations" className="text-sm text-slate-300">Preferred locations</label>
          <Input id="preferred_locations" {...form.register("preferred_locations")} />
        </div>
        <div className="space-y-2">
          <label htmlFor="source_kind" className="text-sm text-slate-300">Source kind</label>
          <select
            id="source_kind"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
            {...form.register("source_kind")}
            disabled={Boolean(selectedPreset)}
          >
            <option value="manual">Manual only</option>
            <option value="greenhouse_board">Greenhouse board</option>
            <option value="lever_board">Lever board</option>
            <option value="workday_board">Workday board</option>
            <option value="direct_url">Direct careers URL</option>
            <option value="jobspy_search">JobSpy multi-board search</option>
          </select>
        </div>
        <div className="space-y-2">
          <label htmlFor="source_preset_key" className="text-sm text-slate-300">Preset source</label>
          <select
            id="source_preset_key"
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
          <label htmlFor="source_label" className="text-sm text-slate-300">Source label</label>
          <Input id="source_label" {...form.register("source_label")} placeholder="Nimbus AI Careers" disabled={Boolean(selectedPreset)} />
        </div>
        {!isJobSpySource ? (
          <div className="space-y-2">
            <label htmlFor="source_url" className="text-sm text-slate-300">Source URL</label>
            <Input
              id="source_url"
              {...form.register("source_url")}
              placeholder="https://boards.greenhouse.io/example"
              disabled={Boolean(selectedPreset)}
            />
          </div>
        ) : null}
        {isJobSpySource && !selectedPreset ? (
          <>
            <div className="space-y-2">
              <label htmlFor="jobspy_sites" className="text-sm text-slate-300">Job boards</label>
              <Input id="jobspy_sites" {...form.register("jobspy_sites")} placeholder="linkedin, indeed, glassdoor, google, zip_recruiter" />
              <p className="text-xs text-slate-400">Supported: linkedin, indeed, glassdoor, google, zip_recruiter, naukri, bayt, bdjobs.</p>
            </div>
            <div className="space-y-2">
              <label htmlFor="jobspy_location" className="text-sm text-slate-300">Search location</label>
              <Input id="jobspy_location" {...form.register("jobspy_location")} placeholder="India, Remote, San Francisco, CA" />
            </div>
            <div className="space-y-2">
              <label htmlFor="jobspy_country_indeed" className="text-sm text-slate-300">Indeed / Glassdoor country</label>
              <Input id="jobspy_country_indeed" {...form.register("jobspy_country_indeed")} placeholder="India, USA, United Arab Emirates" />
            </div>
            <div className="space-y-2">
              <label htmlFor="jobspy_results_wanted" className="text-sm text-slate-300">Results per site</label>
              <Input id="jobspy_results_wanted" {...form.register("jobspy_results_wanted", { valueAsNumber: true })} min={1} max={200} type="number" />
            </div>
            <div className="space-y-2">
              <label htmlFor="jobspy_hours_old" className="text-sm text-slate-300">Hours old</label>
              <Input id="jobspy_hours_old" {...form.register("jobspy_hours_old", { valueAsNumber: true })} min={1} max={720} type="number" />
            </div>
          </>
        ) : null}
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
