"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { api, ApiError } from "@/lib/api";
import type { CandidateProfile } from "@/lib/types";
import { safeJsonParse, stringifyJson } from "@/lib/utils";
import { useAppStore } from "@/store/app-store";

const schema = z.object({
  full_name: z.string().min(2),
  headline: z.string().optional(),
  email: z.string().email().or(z.literal("")),
  phone: z.string().optional(),
  location: z.string().optional(),
  target_role: z.string().optional(),
  preferred_locations: z.string().optional(),
  summary: z.string().min(10),
  skills: z.string(),
  experience_json: z.string(),
  projects_json: z.string(),
  education_json: z.string(),
  certifications_json: z.string(),
  links_json: z.string(),
});

type FormValues = z.infer<typeof schema>;

function profileToForm(profile: CandidateProfile): FormValues {
  return {
    full_name: profile.basics.full_name || "",
    headline: profile.basics.headline || "",
    email: profile.basics.email || "",
    phone: profile.basics.phone || "",
    location: profile.basics.location || "",
    target_role: profile.basics.target_role || "",
    preferred_locations: profile.basics.preferred_locations.join(", "),
    summary: profile.summary,
    skills: profile.skills.join(", "),
    experience_json: stringifyJson(profile.experience),
    projects_json: stringifyJson(profile.projects),
    education_json: stringifyJson(profile.education),
    certifications_json: stringifyJson(profile.certifications),
    links_json: stringifyJson(profile.links),
  };
}

export function ProfileForm() {
  const pushToast = useAppStore((state) => state.pushToast);
  const queryClient = useQueryClient();
  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      try {
        return await api<CandidateProfile>("/profile");
      } catch (error) {
        if (error instanceof ApiError && error.status === 404) {
          return null;
        }
        throw error;
      }
    },
  });

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      full_name: "Alex Builder",
      headline: "Staff-level full-stack engineer",
      email: "alex@example.com",
      phone: "",
      location: "Bengaluru, India",
      target_role: "Senior Full Stack Engineer",
      preferred_locations: "Remote, Bengaluru",
      summary: "Engineer focused on AI-enabled workflows, developer tooling, and product execution.",
      skills: "Python, FastAPI, TypeScript, React, Docker",
      experience_json: stringifyJson([]),
      projects_json: stringifyJson([]),
      education_json: stringifyJson([]),
      certifications_json: stringifyJson([]),
      links_json: stringifyJson([]),
    },
  });

  useEffect(() => {
    if (profileQuery.data) {
      form.reset(profileToForm(profileQuery.data));
    }
  }, [form, profileQuery.data]);

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const payload = {
        basics: {
          full_name: values.full_name,
          headline: values.headline || "",
          email: values.email || null,
          phone: values.phone || "",
          location: values.location || "",
          target_role: values.target_role || "",
          preferred_locations: values.preferred_locations
            ? values.preferred_locations.split(",").map((value) => value.trim()).filter(Boolean)
            : [],
        },
        summary: values.summary,
        skills: values.skills.split(",").map((value) => value.trim()).filter(Boolean),
        experience: safeJsonParse(values.experience_json, []),
        projects: safeJsonParse(values.projects_json, []),
        education: safeJsonParse(values.education_json, []),
        certifications: safeJsonParse(values.certifications_json, []),
        links: safeJsonParse(values.links_json, []),
        preferences: profileQuery.data?.preferences || {},
        saved_answers: profileQuery.data?.saved_answers || {},
        fact_locked: true,
      };

      const method = profileQuery.data ? "PUT" : "POST";
      return api<CandidateProfile>("/profile", { method, body: JSON.stringify(payload) });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      pushToast({ title: "Profile saved", tone: "success" });
    },
    onError: () => pushToast({ title: "Failed to save profile", tone: "error" }),
  });

  return (
    <Card className="space-y-6">
      <div className="space-y-2">
        <CardTitle>Master profile editor</CardTitle>
        <CardDescription>
          ApplyForge keeps a fact-locked canonical profile and derives job-specific versions from it.
        </CardDescription>
      </div>

      <form className="grid gap-4 lg:grid-cols-2" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Full name</label>
          <Input {...form.register("full_name")} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Headline</label>
          <Input {...form.register("headline")} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Email</label>
          <Input {...form.register("email")} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Phone</label>
          <Input {...form.register("phone")} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Location</label>
          <Input {...form.register("location")} />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Target role</label>
          <Input {...form.register("target_role")} />
        </div>
        <div className="space-y-2 lg:col-span-2">
          <label className="text-sm text-slate-300">Preferred locations</label>
          <Input {...form.register("preferred_locations")} placeholder="Remote, Bengaluru, London" />
        </div>
        <div className="space-y-2 lg:col-span-2">
          <label className="text-sm text-slate-300">Summary</label>
          <Textarea {...form.register("summary")} className="min-h-[120px]" />
        </div>
        <div className="space-y-2 lg:col-span-2">
          <label className="text-sm text-slate-300">Skills</label>
          <Input {...form.register("skills")} placeholder="Python, FastAPI, React" />
        </div>
        {[
          ["experience_json", "Experience JSON"],
          ["projects_json", "Projects JSON"],
          ["education_json", "Education JSON"],
          ["certifications_json", "Certifications JSON"],
          ["links_json", "Links JSON"],
        ].map(([field, label]) => (
          <div key={field} className="space-y-2 lg:col-span-2">
            <label className="text-sm text-slate-300">{label}</label>
            <Textarea {...form.register(field as keyof FormValues)} className="min-h-[120px] font-mono text-xs" />
          </div>
        ))}
        <div className="lg:col-span-2">
          <Button disabled={mutation.isPending} type="submit">
            {mutation.isPending ? "Saving…" : "Save profile"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
