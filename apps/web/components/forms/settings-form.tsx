"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import type { InboxConnection, InboxOAuthProvider, ResumeTheme } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

const schema = z.object({
  mode: z.enum(["assisted", "auto", "draft"]),
  pause_on_risk: z.boolean(),
  keyword_focus: z.string(),
  default_theme: z.string(),
});

type FormValues = z.infer<typeof schema>;

export function SettingsForm() {
  const pushToast = useAppStore((state) => state.pushToast);
  const searchParams = useSearchParams();
  const lastInboxToast = useRef<string>("");
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
    },
  });
  const themesQuery = useQuery({ queryKey: ["resume-themes"], queryFn: () => api<ResumeTheme[]>("/resume-themes") });
  const inboxQuery = useQuery({ queryKey: ["inbox-connections"], queryFn: () => api<InboxConnection[]>("/inbox/connections") });
  const oauthProvidersQuery = useQuery({
    queryKey: ["inbox-oauth-providers"],
    queryFn: () => api<InboxOAuthProvider[]>("/inbox/oauth/providers"),
  });

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
    });
  }, [form, settingsQuery.data]);

  useEffect(() => {
    const status = searchParams.get("inbox_status");
    const provider = searchParams.get("provider");
    const message = searchParams.get("message");
    const key = `${status}:${provider}:${message}`;
    if (!status || lastInboxToast.current === key) {
      return;
    }
    lastInboxToast.current = key;
    if (status === "connected") {
      pushToast({ title: `${provider === "outlook" ? "Outlook" : "Gmail"} inbox connected`, tone: "success" });
      return;
    }
    pushToast({ title: message || "Inbox connection failed", tone: "error" });
  }, [pushToast, searchParams]);

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

  const oauthStartMutation = useMutation({
    mutationFn: async (provider: "gmail" | "outlook") =>
      api<{ provider: string; authorization_url: string }>(`/inbox/${provider}/oauth/start?return_to=/settings`),
    onSuccess: () => {
      pushToast({ title: "Redirecting to provider consent", tone: "info" });
    },
    onError: () => pushToast({ title: "Failed to start inbox OAuth", tone: "error" }),
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
          <p className="text-sm text-slate-400">Use provider OAuth to let ApplyForge read recent OTP emails. Tokens stay encrypted at rest and masked in logs.</p>
        </div>
        <div className="grid gap-3 lg:grid-cols-2">
          {oauthProvidersQuery.data?.map((provider) => (
            <div key={provider.provider} className="space-y-3 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-white capitalize">{provider.provider}</p>
                  <p className="text-xs text-slate-400">{provider.redirect_uri}</p>
                </div>
                <Badge tone={provider.configured ? "success" : "warning"}>
                  {provider.configured ? "Ready" : "Needs config"}
                </Badge>
              </div>
              <p className="text-xs text-slate-400">Scopes: {provider.scopes.join(", ")}</p>
              {!provider.configured ? (
                <p className="text-xs text-amber-300">Missing env: {provider.missing_env.join(", ")}</p>
              ) : null}
              <Button
                disabled={oauthStartMutation.isPending || !provider.authorization_enabled}
                onClick={async () => {
                  const result = await oauthStartMutation.mutateAsync(provider.provider as "gmail" | "outlook");
                  window.location.href = result.authorization_url;
                }}
                type="button"
                variant="secondary"
              >
                {oauthStartMutation.isPending ? "Starting…" : `Connect ${provider.provider === "outlook" ? "Outlook" : "Gmail"}`}
              </Button>
            </div>
          ))}
        </div>
        <div className="flex flex-wrap gap-3">
          {inboxQuery.data?.map((connection) => (
            <div key={connection.id} className="flex items-center gap-2 rounded-full border border-white/10 px-3 py-2 text-sm text-slate-200">
              <Badge tone="success">{connection.provider}</Badge>
              <span>{connection.email}</span>
              <span className="text-slate-500">
                {String(connection.metadata_json.connected_via || "manual")} · {connection.token_masked}
              </span>
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
