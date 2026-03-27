"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import type { Job } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

const schema = z.object({
  title: z.string().min(2),
  company: z.string().min(2),
  location: z.string().optional(),
  application_url: z.string().url().or(z.literal("")),
  description: z.string().min(20),
  salary: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function JobCreateForm({ onCreated }: { onCreated: (job: Job) => void }) {
  const pushToast = useAppStore((state) => state.pushToast);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: "Senior Full Stack Engineer",
      company: "Nimbus AI",
      location: "Remote, US",
      application_url: "https://example.com/apply",
      description:
        "Looking for Python, FastAPI, React, TypeScript, and Docker experience. AI product delivery is a plus.",
      salary: "$150k - $180k",
    },
  });

  const mutation = useMutation({
    mutationFn: async (values: FormValues) =>
      api<Job>("/jobs/manual", {
        method: "POST",
        body: JSON.stringify({
          ...values,
          remote_type: values.location?.toLowerCase().includes("remote") ? "remote" : "unknown",
          source: "manual",
          seniority: "",
          employment_type: "",
          visa_support: "unknown",
          tags: [],
        }),
      }),
    onSuccess: (job) => {
      pushToast({ title: "Job added to your pipeline", tone: "success" });
      onCreated(job);
      reset();
    },
    onError: () => pushToast({ title: "Failed to create job", tone: "error" }),
  });

  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <CardTitle>Add a job manually</CardTitle>
        <CardDescription>Paste a job description or capture a role you found elsewhere.</CardDescription>
      </div>
      <form className="grid gap-4 lg:grid-cols-2" onSubmit={handleSubmit((values) => mutation.mutate(values))}>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Role</label>
          <Input {...register("title")} />
          {errors.title ? <p className="text-xs text-rose-300">{errors.title.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Company</label>
          <Input {...register("company")} />
          {errors.company ? <p className="text-xs text-rose-300">{errors.company.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Location</label>
          <Input {...register("location")} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Application URL</label>
          <Input {...register("application_url")} />
          {errors.application_url ? <p className="text-xs text-rose-300">{errors.application_url.message}</p> : null}
        </div>
        <div className="space-y-2 lg:col-span-2">
          <label className="text-sm text-slate-300">Description</label>
          <Textarea {...register("description")} className="min-h-[180px]" />
          {errors.description ? <p className="text-xs text-rose-300">{errors.description.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Salary</label>
          <Input {...register("salary")} />
        </div>
        <div className="flex items-end">
          <Button className="w-full" disabled={mutation.isPending} type="submit">
            {mutation.isPending ? "Saving…" : "Add job"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
