"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useId } from "react";
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
  const roleStrategyId = useId();
  const roleId = useId();
  const roleErrorId = useId();
  const companyId = useId();
  const companyErrorId = useId();
  const locationId = useId();
  const urlId = useId();
  const urlErrorId = useId();
  const descriptionId = useId();
  const descriptionErrorId = useId();
  const salaryId = useId();

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
          <label htmlFor={roleStrategyId} className="text-sm text-slate-300">Role strategy</label>
          <select
            id={roleStrategyId}
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
          <label htmlFor={roleId} className="text-sm text-slate-300">Role</label>
          <Input
            id={roleId}
            {...register("title")}
            aria-invalid={!!errors.title}
            aria-describedby={errors.title ? roleErrorId : undefined}
          />
          {errors.title ? <p id={roleErrorId} role="alert" className="text-xs text-rose-300">{errors.title.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label htmlFor={companyId} className="text-sm text-slate-300">Company</label>
          <Input
            id={companyId}
            {...register("company")}
            aria-invalid={!!errors.company}
            aria-describedby={errors.company ? companyErrorId : undefined}
          />
          {errors.company ? <p id={companyErrorId} role="alert" className="text-xs text-rose-300">{errors.company.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label htmlFor={locationId} className="text-sm text-slate-300">Location</label>
          <Input id={locationId} {...register("location")} />
        </div>
        <div className="space-y-2">
          <label htmlFor={urlId} className="text-sm text-slate-300">Application URL</label>
          <Input
            id={urlId}
            {...register("application_url")}
            aria-invalid={!!errors.application_url}
            aria-describedby={errors.application_url ? urlErrorId : undefined}
          />
          {errors.application_url ? <p id={urlErrorId} role="alert" className="text-xs text-rose-300">{errors.application_url.message}</p> : null}
        </div>
        <div className="space-y-2 lg:col-span-2">
          <label htmlFor={descriptionId} className="text-sm text-slate-300">Description</label>
          <Textarea
            id={descriptionId}
            {...register("description")}
            className="min-h-[180px]"
            aria-invalid={!!errors.description}
            aria-describedby={errors.description ? descriptionErrorId : undefined}
          />
          {errors.description ? <p id={descriptionErrorId} role="alert" className="text-xs text-rose-300">{errors.description.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label htmlFor={salaryId} className="text-sm text-slate-300">Salary</label>
          <Input id={salaryId} {...register("salary")} />
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
