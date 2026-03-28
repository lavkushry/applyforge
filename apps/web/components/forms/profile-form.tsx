"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ReactNode, useEffect } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { api, ApiError } from "@/lib/api";
import type { CandidateProfile } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

const experienceItemSchema = z.object({
  title: z.string(),
  company: z.string(),
  start_date: z.string(),
  end_date: z.string(),
  highlights_text: z.string(),
});

const projectItemSchema = z.object({
  name: z.string(),
  highlights_text: z.string(),
});

const educationItemSchema = z.object({
  institution: z.string(),
  degree: z.string(),
});

const certificationItemSchema = z.object({
  name: z.string(),
  issuer: z.string(),
});

const linkItemSchema = z.object({
  label: z.string(),
  url: z.string(),
});

const schema = z.object({
  full_name: z.string().min(2, "Add a full name"),
  headline: z.string().optional(),
  email: z.string().email("Use a valid email").or(z.literal("")),
  phone: z.string().optional(),
  location: z.string().optional(),
  target_role: z.string().optional(),
  preferred_locations: z.string().optional(),
  summary: z.string().min(10, "Add a stronger profile summary"),
  skills: z.string(),
  work_authorization: z.string().optional(),
  remote_preference: z.string().optional(),
  willing_to_relocate: z.string().optional(),
  requires_sponsorship: z.string().optional(),
  notice_period: z.string().optional(),
  salary_expectation: z.string().optional(),
  years_of_experience: z.string().optional(),
  available_start_date: z.string().optional(),
  authorized_to_work: z.string().optional(),
  experience: z.array(experienceItemSchema),
  projects: z.array(projectItemSchema),
  education: z.array(educationItemSchema),
  certifications: z.array(certificationItemSchema),
  links: z.array(linkItemSchema),
});

type FormValues = z.infer<typeof schema>;

const blankExperience = () => ({
  title: "",
  company: "",
  start_date: "",
  end_date: "",
  highlights_text: "",
});

const blankProject = () => ({
  name: "",
  highlights_text: "",
});

const blankEducation = () => ({
  institution: "",
  degree: "",
});

const blankCertification = () => ({
  name: "",
  issuer: "",
});

const blankLink = () => ({
  label: "",
  url: "",
});

function linesFromText(value: string): string[] {
  return value
    .split("\n")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function profileToForm(profile: CandidateProfile): FormValues {
  const preferences = profile.preferences || {};
  const savedAnswers = profile.saved_answers || {};
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
    work_authorization: String(preferences["work_authorization"] || ""),
    remote_preference: String(preferences["remote_preference"] || ""),
    willing_to_relocate: String(savedAnswers["willing_to_relocate"] || preferences["willing_to_relocate"] || ""),
    requires_sponsorship: String(savedAnswers["requires_sponsorship"] || preferences["requires_sponsorship"] || ""),
    notice_period: String(savedAnswers["notice_period"] || ""),
    salary_expectation: String(savedAnswers["salary_expectation"] || ""),
    years_of_experience: String(savedAnswers["years_of_experience"] || ""),
    available_start_date: String(savedAnswers["available_start_date"] || ""),
    authorized_to_work: String(savedAnswers["authorized_to_work"] || ""),
    experience: profile.experience.length
      ? profile.experience.map((item) => ({
          title: item.title || "",
          company: item.company || "",
          start_date: item.start_date || "",
          end_date: item.end_date || "",
          highlights_text: (item.highlights || []).join("\n"),
        }))
      : [blankExperience()],
    projects: profile.projects.length
      ? profile.projects.map((item) => ({
          name: item.name || "",
          highlights_text: (item.highlights || []).join("\n"),
        }))
      : [blankProject()],
    education: profile.education.length
      ? profile.education.map((item) => ({
          institution: item.institution || "",
          degree: item.degree || "",
        }))
      : [blankEducation()],
    certifications: profile.certifications.length
      ? profile.certifications.map((item) => ({
          name: item.name || "",
          issuer: item.issuer || "",
        }))
      : [blankCertification()],
    links: profile.links.length
      ? profile.links.map((item) => ({
          label: item.label || "",
          url: item.url || "",
        }))
      : [blankLink()],
  };
}

function compactExperience(values: FormValues["experience"]) {
  return values
    .map((item) => ({
      title: item.title.trim(),
      company: item.company.trim(),
      start_date: item.start_date.trim(),
      end_date: item.end_date.trim(),
      highlights: linesFromText(item.highlights_text),
    }))
    .filter((item) => item.title || item.company || item.start_date || item.end_date || item.highlights.length);
}

function compactProjects(values: FormValues["projects"]) {
  return values
    .map((item) => ({
      name: item.name.trim(),
      highlights: linesFromText(item.highlights_text),
    }))
    .filter((item) => item.name || item.highlights.length);
}

function compactEducation(values: FormValues["education"]) {
  return values
    .map((item) => ({
      institution: item.institution.trim(),
      degree: item.degree.trim(),
    }))
    .filter((item) => item.institution || item.degree);
}

function compactCertifications(values: FormValues["certifications"]) {
  return values
    .map((item) => ({
      name: item.name.trim(),
      issuer: item.issuer.trim(),
    }))
    .filter((item) => item.name || item.issuer);
}

function compactLinks(values: FormValues["links"]) {
  return values
    .map((item) => ({
      label: item.label.trim(),
      url: item.url.trim(),
    }))
    .filter((item) => item.label || item.url);
}

function FieldError({ message }: { message?: string }) {
  if (!message) {
    return null;
  }
  return <p className="text-xs text-rose-300">{message}</p>;
}

function SectionHeader({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="space-y-1">
        <h3 className="text-base font-semibold text-white">{title}</h3>
        <p className="text-sm text-slate-400">{description}</p>
      </div>
      {action}
    </div>
  );
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
      work_authorization: "Authorized to work in the United States",
      remote_preference: "remote",
      willing_to_relocate: "yes",
      requires_sponsorship: "no",
      notice_period: "Two weeks",
      salary_expectation: "",
      years_of_experience: "",
      available_start_date: "",
      authorized_to_work: "yes",
      experience: [blankExperience()],
      projects: [blankProject()],
      education: [blankEducation()],
      certifications: [blankCertification()],
      links: [blankLink()],
    },
  });

  const experienceFields = useFieldArray({ control: form.control, name: "experience" });
  const projectFields = useFieldArray({ control: form.control, name: "projects" });
  const educationFields = useFieldArray({ control: form.control, name: "education" });
  const certificationFields = useFieldArray({ control: form.control, name: "certifications" });
  const linkFields = useFieldArray({ control: form.control, name: "links" });

  useEffect(() => {
    if (profileQuery.data) {
      form.reset(profileToForm(profileQuery.data));
    }
  }, [form, profileQuery.data]);

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const payload = {
        basics: {
          full_name: values.full_name.trim(),
          headline: (values.headline || "").trim(),
          email: values.email || null,
          phone: (values.phone || "").trim(),
          location: (values.location || "").trim(),
          target_role: (values.target_role || "").trim(),
          preferred_locations: values.preferred_locations
            ? values.preferred_locations.split(",").map((value) => value.trim()).filter(Boolean)
            : [],
        },
        summary: values.summary.trim(),
        skills: values.skills
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean),
        experience: compactExperience(values.experience),
        projects: compactProjects(values.projects),
        education: compactEducation(values.education),
        certifications: compactCertifications(values.certifications),
        links: compactLinks(values.links),
        preferences: {
          ...(profileQuery.data?.preferences || {}),
          work_authorization: (values.work_authorization || "").trim(),
          remote_preference: (values.remote_preference || "").trim(),
          willing_to_relocate: (values.willing_to_relocate || "").trim(),
          requires_sponsorship: (values.requires_sponsorship || "").trim(),
        },
        saved_answers: {
          ...(profileQuery.data?.saved_answers || {}),
          notice_period: (values.notice_period || "").trim(),
          salary_expectation: (values.salary_expectation || "").trim(),
          years_of_experience: (values.years_of_experience || "").trim(),
          available_start_date: (values.available_start_date || "").trim(),
          authorized_to_work: (values.authorized_to_work || "").trim(),
          willing_to_relocate: (values.willing_to_relocate || "").trim(),
          requires_sponsorship: (values.requires_sponsorship || "").trim(),
        },
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
          Maintain a clean canonical profile with structured career history, links, and application answers instead of raw JSON blobs.
        </CardDescription>
      </div>

      <form className="space-y-6" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm text-slate-300">Full name</label>
            <Input {...form.register("full_name")} />
            <FieldError message={form.formState.errors.full_name?.message} />
          </div>
          <div className="space-y-2">
            <label className="text-sm text-slate-300">Headline</label>
            <Input {...form.register("headline")} />
          </div>
          <div className="space-y-2">
            <label className="text-sm text-slate-300">Email</label>
            <Input {...form.register("email")} />
            <FieldError message={form.formState.errors.email?.message} />
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
            <Textarea {...form.register("summary")} className="min-h-[140px]" />
            <FieldError message={form.formState.errors.summary?.message} />
          </div>
          <div className="space-y-2 lg:col-span-2">
            <label className="text-sm text-slate-300">Skills</label>
            <Input {...form.register("skills")} placeholder="Python, FastAPI, React, Playwright" />
          </div>
        </div>

        <Card className="space-y-4 border-white/5 bg-slate-950/60">
          <SectionHeader title="Application preferences" description="These answers power auto-fill, scoring, and policy gating." />
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Work authorization</label>
              <Input {...form.register("work_authorization")} placeholder="Authorized to work in the United States" />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Remote preference</label>
              <Input {...form.register("remote_preference")} placeholder="remote, hybrid, onsite" />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Willing to relocate</label>
              <Input {...form.register("willing_to_relocate")} placeholder="yes or no" />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Requires sponsorship</label>
              <Input {...form.register("requires_sponsorship")} placeholder="yes or no" />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Notice period</label>
              <Input {...form.register("notice_period")} placeholder="Two weeks" />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Salary expectation</label>
              <Input {...form.register("salary_expectation")} placeholder="$180,000" />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Years of experience</label>
              <Input {...form.register("years_of_experience")} placeholder="8" />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Available start date</label>
              <Input {...form.register("available_start_date")} placeholder="2026-04-15" />
            </div>
            <div className="space-y-2 lg:col-span-2">
              <label className="text-sm text-slate-300">Authorized to work answer</label>
              <Input {...form.register("authorized_to_work")} placeholder="yes or no" />
            </div>
          </div>
        </Card>

        <Card className="space-y-4 border-white/5 bg-slate-950/60">
          <SectionHeader
            title="Experience"
            description="Capture only factual roles and impact bullets."
            action={
              <Button onClick={() => experienceFields.append(blankExperience())} type="button" variant="secondary">
                Add role
              </Button>
            }
          />
          <div className="space-y-4">
            {experienceFields.fields.map((field, index) => (
              <div key={field.id} className="space-y-3 rounded-2xl border border-white/10 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium text-white">Role {index + 1}</p>
                  {experienceFields.fields.length > 1 ? (
                    <Button onClick={() => experienceFields.remove(index)} type="button" variant="ghost">
                      Remove
                    </Button>
                  ) : null}
                </div>
                <div className="grid gap-3 lg:grid-cols-2">
                  <Input {...form.register(`experience.${index}.title`)} placeholder="Staff Engineer" />
                  <Input {...form.register(`experience.${index}.company`)} placeholder="Forge Labs" />
                  <Input {...form.register(`experience.${index}.start_date`)} placeholder="2021-01" />
                  <Input {...form.register(`experience.${index}.end_date`)} placeholder="Present" />
                </div>
                <Textarea
                  {...form.register(`experience.${index}.highlights_text`)}
                  className="min-h-[120px]"
                  placeholder={"One highlight per line\nBuilt workflow automation\nOwned platform reliability"}
                />
              </div>
            ))}
          </div>
        </Card>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="space-y-4 border-white/5 bg-slate-950/60">
            <SectionHeader
              title="Projects"
              description="Keep project evidence that can be pulled into tailored resumes."
              action={
                <Button onClick={() => projectFields.append(blankProject())} type="button" variant="secondary">
                  Add project
                </Button>
              }
            />
            <div className="space-y-4">
              {projectFields.fields.map((field, index) => (
                <div key={field.id} className="space-y-3 rounded-2xl border border-white/10 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-medium text-white">Project {index + 1}</p>
                    {projectFields.fields.length > 1 ? (
                      <Button onClick={() => projectFields.remove(index)} type="button" variant="ghost">
                        Remove
                      </Button>
                    ) : null}
                  </div>
                  <Input {...form.register(`projects.${index}.name`)} placeholder="ApplyForge" />
                  <Textarea
                    {...form.register(`projects.${index}.highlights_text`)}
                    className="min-h-[120px]"
                    placeholder={"One highlight per line\nBuilt a role-based job feed\nImplemented Playwright-assisted apply"}
                  />
                </div>
              ))}
            </div>
          </Card>

          <Card className="space-y-4 border-white/5 bg-slate-950/60">
            <SectionHeader
              title="Education"
              description="Use concise entries for schools and degrees."
              action={
                <Button onClick={() => educationFields.append(blankEducation())} type="button" variant="secondary">
                  Add education
                </Button>
              }
            />
            <div className="space-y-4">
              {educationFields.fields.map((field, index) => (
                <div key={field.id} className="grid gap-3 rounded-2xl border border-white/10 p-4 lg:grid-cols-[1fr_1fr_auto]">
                  <Input {...form.register(`education.${index}.institution`)} placeholder="University name" />
                  <Input {...form.register(`education.${index}.degree`)} placeholder="Degree or program" />
                  {educationFields.fields.length > 1 ? (
                    <Button onClick={() => educationFields.remove(index)} type="button" variant="ghost">
                      Remove
                    </Button>
                  ) : (
                    <div />
                  )}
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="space-y-4 border-white/5 bg-slate-950/60">
            <SectionHeader
              title="Certifications"
              description="Store concise certification records for reuse."
              action={
                <Button onClick={() => certificationFields.append(blankCertification())} type="button" variant="secondary">
                  Add certification
                </Button>
              }
            />
            <div className="space-y-4">
              {certificationFields.fields.map((field, index) => (
                <div key={field.id} className="grid gap-3 rounded-2xl border border-white/10 p-4 lg:grid-cols-[1fr_1fr_auto]">
                  <Input {...form.register(`certifications.${index}.name`)} placeholder="AWS Certified Developer" />
                  <Input {...form.register(`certifications.${index}.issuer`)} placeholder="Amazon Web Services" />
                  {certificationFields.fields.length > 1 ? (
                    <Button onClick={() => certificationFields.remove(index)} type="button" variant="ghost">
                      Remove
                    </Button>
                  ) : (
                    <div />
                  )}
                </div>
              ))}
            </div>
          </Card>

          <Card className="space-y-4 border-white/5 bg-slate-950/60">
            <SectionHeader
              title="Links"
              description="LinkedIn, GitHub, portfolio, and other public proof points."
              action={
                <Button onClick={() => linkFields.append(blankLink())} type="button" variant="secondary">
                  Add link
                </Button>
              }
            />
            <div className="space-y-4">
              {linkFields.fields.map((field, index) => (
                <div key={field.id} className="grid gap-3 rounded-2xl border border-white/10 p-4 lg:grid-cols-[0.9fr_1.1fr_auto]">
                  <Input {...form.register(`links.${index}.label`)} placeholder="LinkedIn" />
                  <Input {...form.register(`links.${index}.url`)} placeholder="https://linkedin.com/in/you" />
                  {linkFields.fields.length > 1 ? (
                    <Button onClick={() => linkFields.remove(index)} type="button" variant="ghost">
                      Remove
                    </Button>
                  ) : (
                    <div />
                  )}
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="flex items-center justify-between gap-4 rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-4">
          <div className="space-y-1">
            <p className="text-sm font-medium text-white">Fact-locked profile</p>
            <p className="text-sm text-slate-300">Only store facts you can defend in an interview. Tailoring depends on this canonical record.</p>
          </div>
          <Button disabled={mutation.isPending} type="submit">
            {mutation.isPending ? "Saving…" : "Save profile"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
