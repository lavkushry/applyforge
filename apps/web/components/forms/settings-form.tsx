"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAppStore } from "@/store/app-store";

const schema = z.object({
  mode: z.enum(["assisted", "auto", "draft"]),
  pause_on_risk: z.boolean(),
  keyword_focus: z.string(),
});

type FormValues = z.infer<typeof schema>;

export function SettingsForm() {
  const pushToast = useAppStore((state) => state.pushToast);
  const settingsQuery = useQuery({
    queryKey: ["settings"],
    queryFn: () => api<Record<string, unknown>>("/profile/settings"),
  });

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      mode: "assisted",
      pause_on_risk: true,
      keyword_focus: "python, ai, fastapi",
    },
  });

  useEffect(() => {
    const automation = settingsQuery.data?.automation_preferences as Record<string, unknown> | undefined;
    const filters = settingsQuery.data?.job_filters as Record<string, unknown> | undefined;
    if (!automation && !filters) {
      return;
    }
    form.reset({
      mode: (automation?.mode as FormValues["mode"]) || "assisted",
      pause_on_risk: Boolean(automation?.pause_on_risk ?? true),
      keyword_focus: Array.isArray(filters?.keyword_focus)
        ? (filters?.keyword_focus as string[]).join(", ")
        : "python, ai, fastapi",
    });
  }, [form, settingsQuery.data]);

  const mutation = useMutation({
    mutationFn: async (values: FormValues) =>
      api("/profile/settings", {
        method: "PUT",
        body: JSON.stringify({
          values: {
            automation_preferences: {
              mode: values.mode,
              pause_on_risk: values.pause_on_risk,
            },
            job_filters: {
              keyword_focus: values.keyword_focus.split(",").map((value) => value.trim()).filter(Boolean),
            },
          },
        }),
      }),
    onSuccess: () => pushToast({ title: "Settings saved", tone: "success" }),
    onError: () => pushToast({ title: "Failed to save settings", tone: "error" }),
  });

  return (
    <Card className="space-y-6">
      <div className="space-y-2">
        <CardTitle>Automation preferences</CardTitle>
        <CardDescription>Keep risky questions gated while preparing faster repeatable apply flows.</CardDescription>
      </div>

      <form className="space-y-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Default mode</label>
          <select
            className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
            {...form.register("mode")}
          >
            <option value="assisted">Assisted apply</option>
            <option value="auto">Auto apply</option>
            <option value="draft">Draft mode</option>
          </select>
        </div>

        <label className="flex items-center gap-3 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200">
          <input type="checkbox" {...form.register("pause_on_risk")} />
          Pause automation when risky questions are detected
        </label>

        <div className="space-y-2">
          <label className="text-sm text-slate-300">Priority keywords</label>
          <Input {...form.register("keyword_focus")} />
        </div>

        <Button disabled={mutation.isPending} type="submit">
          {mutation.isPending ? "Saving…" : "Save preferences"}
        </Button>
      </form>
    </Card>
  );
}
