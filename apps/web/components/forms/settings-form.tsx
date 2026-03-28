"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import type { InboxConnection, ResumeTheme } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

const schema = z.object({
  mode: z.enum(["assisted", "auto", "draft"]),
  pause_on_risk: z.boolean(),
  keyword_focus: z.string(),
  default_theme: z.string(),
  inbox_provider: z.enum(["gmail", "outlook"]),
  inbox_email: z.string().email(),
  inbox_token: z.string().min(8),
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
      default_theme: "classic-ats-light",
      inbox_provider: "gmail",
      inbox_email: "candidate@example.com",
      inbox_token: "oauth-demo-token",
    },
  });
  const themesQuery = useQuery({ queryKey: ["resume-themes"], queryFn: () => api<ResumeTheme[]>("/resume-themes") });
  const inboxQuery = useQuery({ queryKey: ["inbox-connections"], queryFn: () => api<InboxConnection[]>("/inbox/connections") });

  useEffect(() => {
    const automation = settingsQuery.data?.automation_preferences as Record<string, unknown> | undefined;
    const filters = settingsQuery.data?.job_filters as Record<string, unknown> | undefined;
    const resume = settingsQuery.data?.resume_preferences as Record<string, unknown> | undefined;
    if (!automation && !filters && !resume) {
      return;
    }
    form.reset({
      mode: (automation?.mode as FormValues["mode"]) || "assisted",
      pause_on_risk: Boolean(automation?.pause_on_risk ?? true),
      keyword_focus: Array.isArray(filters?.keyword_focus)
        ? (filters?.keyword_focus as string[]).join(", ")
        : "python, ai, fastapi",
      default_theme: (resume?.default_theme as string) || "classic-ats-light",
      inbox_provider: "gmail",
      inbox_email: "candidate@example.com",
      inbox_token: "oauth-demo-token",
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
            resume_preferences: {
              default_theme: values.default_theme,
              ats_mode: true,
            },
          },
        }),
      }),
    onSuccess: () => pushToast({ title: "Settings saved", tone: "success" }),
    onError: () => pushToast({ title: "Failed to save settings", tone: "error" }),
  });

  const inboxMutation = useMutation({
    mutationFn: async (values: FormValues) =>
      api<InboxConnection>(`/inbox/${values.inbox_provider}/connect`, {
        method: "POST",
        body: JSON.stringify({
          provider: values.inbox_provider,
          email: values.inbox_email,
          token: values.inbox_token,
          scopes: ["mail.read", "mail.metadata"],
        }),
      }),
    onSuccess: () => {
      pushToast({ title: "Inbox connected", tone: "success" });
      inboxQuery.refetch();
    },
    onError: () => pushToast({ title: "Inbox connection failed", tone: "error" }),
  });

  const disconnectMutation = useMutation({
    mutationFn: async (connectionId: number) => api(`/inbox/connections/${connectionId}`, { method: "DELETE" }),
    onSuccess: () => {
      pushToast({ title: "Inbox disconnected", tone: "info" });
      inboxQuery.refetch();
    },
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

        <div className="space-y-2">
          <label className="text-sm text-slate-300">Default resume theme</label>
          <select
            className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
            {...form.register("default_theme")}
          >
            {themesQuery.data?.map((theme) => (
              <option key={theme.id} value={theme.slug}>
                {theme.label}
              </option>
            ))}
          </select>
        </div>

        <Button disabled={mutation.isPending} type="submit">
          {mutation.isPending ? "Saving…" : "Save preferences"}
        </Button>
      </form>

      <div className="space-y-4 rounded-2xl border border-white/10 bg-slate-950/50 p-4">
        <div className="space-y-1">
          <p className="text-sm font-medium text-white">Inbox OTP access</p>
          <p className="text-sm text-slate-400">Gmail and Outlook OAuth-style connections only. OTP codes stay masked in logs.</p>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          <select
            className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
            {...form.register("inbox_provider")}
          >
            <option value="gmail">Gmail</option>
            <option value="outlook">Outlook</option>
          </select>
          <Input {...form.register("inbox_email")} placeholder="name@example.com" />
          <Input {...form.register("inbox_token")} placeholder="OAuth token" />
        </div>
        <div className="flex flex-wrap gap-3">
          <Button
            disabled={inboxMutation.isPending}
            onClick={form.handleSubmit((values) => inboxMutation.mutate(values))}
            type="button"
            variant="secondary"
          >
            {inboxMutation.isPending ? "Connecting…" : "Connect inbox"}
          </Button>
          {inboxQuery.data?.map((connection) => (
            <div key={connection.id} className="flex items-center gap-2 rounded-full border border-white/10 px-3 py-2 text-sm text-slate-200">
              <Badge tone="success">{connection.provider}</Badge>
              <span>{connection.email}</span>
              <span className="text-slate-500">{connection.token_masked}</span>
              <Button type="button" variant="ghost" onClick={() => disconnectMutation.mutate(connection.id)}>
                Disconnect
              </Button>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
