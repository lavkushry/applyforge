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
import type { Job, TargetRole } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

const schema = z.object({
  role_id: z.string().default(""),
  title: z.string().min(2),
  company: z.string().min(2),
  location: z.string().optional(),
  application_url: z.string().url().or(z.literal("")),
  description: z.string().min(20),
  salary: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function JobCreateForm({ onCreated, roles }: { onCreated: (job: Job) => void; roles: TargetRole[] }) {
  const pushToast = useAppStore((state) => state.pushToast);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      role_id: "",
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
          role_id: values.role_id ? Number(values.role_id) : null,
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
          <label htmlFor="role_id" className="text-sm text-slate-300">Role strategy</label>
          <select
            id="role_id"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
            {...register("role_id")}
          >
            <option value="">No linked role</option>
            {roles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          <label htmlFor="title" className="text-sm text-slate-300">Role</label>
          <Input
            id="title"
            {...register("title")}
            aria-invalid={!!errors.title}
            aria-describedby={errors.title ? "title-error" : undefined}
          />
          {errors.title ? <p id="title-error" role="alert" className="text-xs text-rose-300">{errors.title.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label htmlFor="company" className="text-sm text-slate-300">Company</label>
          <Input
            id="company"
            {...register("company")}
            aria-invalid={!!errors.company}
            aria-describedby={errors.company ? "company-error" : undefined}
          />
          {errors.company ? <p id="company-error" role="alert" className="text-xs text-rose-300">{errors.company.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label htmlFor="location" className="text-sm text-slate-300">Location</label>
          <Input id="location" {...register("location")} />
        </div>
        <div className="space-y-2">
          <label htmlFor="application_url" className="text-sm text-slate-300">Application URL</label>
          <Input
            id="application_url"
            {...register("application_url")}
            aria-invalid={!!errors.application_url}
            aria-describedby={errors.application_url ? "application_url-error" : undefined}
          />
          {errors.application_url ? <p id="application_url-error" role="alert" className="text-xs text-rose-300">{errors.application_url.message}</p> : null}
        </div>
        <div className="space-y-2 lg:col-span-2">
          <label htmlFor="description" className="text-sm text-slate-300">Description</label>
          <Textarea
            id="description"
            {...register("description")}
            className="min-h-[180px]"
            aria-invalid={!!errors.description}
            aria-describedby={errors.description ? "description-error" : undefined}
          />
          {errors.description ? <p id="description-error" role="alert" className="text-xs text-rose-300">{errors.description.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label htmlFor="salary" className="text-sm text-slate-300">Salary</label>
          <Input id="salary" {...register("salary")} />
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
