"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";
import { Textarea } from "@/components/ui/textarea";
import { api, ApiError } from "@/lib/api";
import type { Company, CompanyContact, CompanyDetail, CompanyPortal, IngestionRun, Job, TargetRole } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

const emptyCompany = {
  name: "",
  website_url: "",
  careers_url: "",
  linkedin_url: "",
  hq_location: "",
  industry: "",
  notes: "",
  active: true,
};

const emptyPortal = {
  provider_kind: "greenhouse",
  base_url: "",
  board_token: "",
  health_status: "unknown",
  supports_structured_fetch: true,
  notes: "",
};

const emptyContact = {
  full_name: "",
  title: "",
  email: "",
  linkedin_url: "",
  contact_type: "recruiter",
  source: "manual",
  source_url: "",
  confidence: 0.8,
  notes: "",
};

const emptyCompanies: Company[] = [];
const emptyJobs: Job[] = [];
const emptyRuns: IngestionRun[] = [];
const emptyRoles: TargetRole[] = [];

function formatTimestamp(value: string | null | undefined): string {
  if (!value) {
    return "Never";
  }
  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return value;
  }
  return timestamp.toLocaleString();
}

function describeApiError(error: unknown, fallback: string): string {
  if (!(error instanceof ApiError)) {
    return fallback;
  }
  try {
    const payload = JSON.parse(error.message) as { detail?: string };
    return payload.detail || fallback;
  } catch {
    return error.message || fallback;
  }
}

export default function CompaniesPage() {
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
  const [selectedRoleId, setSelectedRoleId] = useState<string>("");
  const [selectedPortalId, setSelectedPortalId] = useState<string>("");
  const [companyForm, setCompanyForm] = useState(emptyCompany);
  const [portalForm, setPortalForm] = useState(emptyPortal);
  const [contactForm, setContactForm] = useState(emptyContact);
  const pushToast = useAppStore((state) => state.pushToast);
  const queryClient = useQueryClient();

  const companiesQuery = useQuery({
    queryKey: ["companies"],
    queryFn: () => api<Company[]>("/companies"),
  });

  const companies = companiesQuery.data ?? emptyCompanies;
  const rolesQuery = useQuery({
    queryKey: ["roles"],
    queryFn: () => api<TargetRole[]>("/roles"),
  });
  const roles = rolesQuery.data ?? emptyRoles;

  useEffect(() => {
    if (!companies.length) {
      setSelectedCompanyId(null);
      return;
    }
    if (!selectedCompanyId || !companies.some((company) => company.id === selectedCompanyId)) {
      setSelectedCompanyId(companies[0].id);
    }
  }, [companies, selectedCompanyId]);

  useEffect(() => {
    if (!roles.length) {
      setSelectedRoleId("");
      return;
    }
    if (!selectedRoleId || !roles.some((role) => String(role.id) === selectedRoleId)) {
      setSelectedRoleId(String(roles[0].id));
    }
  }, [roles, selectedRoleId]);

  const companyDetailQuery = useQuery({
    queryKey: ["company", selectedCompanyId],
    queryFn: () => api<CompanyDetail>(`/companies/${selectedCompanyId}`),
    enabled: Boolean(selectedCompanyId),
  });

  const linkedJobsQuery = useQuery({
    queryKey: ["company-jobs", selectedCompanyId],
    queryFn: () => api<Job[]>(`/jobs?company_id=${selectedCompanyId}`),
    enabled: Boolean(selectedCompanyId),
  });
  const companyRunsQuery = useQuery({
    queryKey: ["company-ingestion-runs", selectedCompanyId],
    queryFn: () => api<IngestionRun[]>(`/companies/${selectedCompanyId}/ingestion-runs`),
    enabled: Boolean(selectedCompanyId),
  });

  const createCompanyMutation = useMutation({
    mutationFn: (payload: typeof emptyCompany) =>
      api<Company>("/companies", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: (company) => {
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      setSelectedCompanyId(company.id);
      setCompanyForm(emptyCompany);
      pushToast({ title: "Company saved", tone: "success" });
    },
    onError: () => pushToast({ title: "Failed to save company", tone: "error" }),
  });

  const createPortalMutation = useMutation({
    mutationFn: (payload: typeof emptyPortal) => {
      if (!selectedCompanyId) {
        throw new Error("No company selected");
      }
      return api<CompanyPortal>(`/companies/${selectedCompanyId}/portals`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["company", selectedCompanyId] });
      setPortalForm(emptyPortal);
      pushToast({ title: "Company portal added", tone: "success" });
    },
    onError: () => pushToast({ title: "Failed to add portal", tone: "error" }),
  });

  const createContactMutation = useMutation({
    mutationFn: (payload: typeof emptyContact) => {
      if (!selectedCompanyId) {
        throw new Error("No company selected");
      }
      return api<CompanyContact>(`/companies/${selectedCompanyId}/contacts`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["company", selectedCompanyId] });
      setContactForm(emptyContact);
      pushToast({ title: "Company contact added", tone: "success" });
    },
    onError: () => pushToast({ title: "Failed to add contact", tone: "error" }),
  });
  const resolvePortalsMutation = useMutation({
    mutationFn: () => {
      if (!selectedCompanyId) {
        throw new Error("No company selected");
      }
      return api<CompanyPortal[]>(`/companies/${selectedCompanyId}/resolve-portals`, { method: "POST" });
    },
    onSuccess: (portals) => {
      queryClient.invalidateQueries({ queryKey: ["company", selectedCompanyId] });
      if (!selectedPortalId && portals.length === 1) {
        setSelectedPortalId(String(portals[0].id));
      }
      if (!portals.length) {
        pushToast({ title: "No portals resolved from the current careers URL", tone: "info" });
        return;
      }
      pushToast({ title: `Resolved ${portals.length} portal${portals.length === 1 ? "" : "s"}`, tone: "success" });
    },
    onError: (error) => pushToast({ title: describeApiError(error, "Failed to resolve portals"), tone: "error" }),
  });
  const scrapeCompanyMutation = useMutation({
    mutationFn: () => {
      if (!selectedCompanyId) {
        throw new Error("No company selected");
      }
      if (!selectedRoleId) {
        throw new Error("No role selected");
      }
      return api<IngestionRun>(`/companies/${selectedCompanyId}/scrape-now`, {
        method: "POST",
        body: JSON.stringify({
          role_id: Number(selectedRoleId),
          ...(selectedPortalId ? { portal_id: Number(selectedPortalId) } : {}),
        }),
      });
    },
    onSuccess: (run) => {
      queryClient.invalidateQueries({ queryKey: ["company", selectedCompanyId] });
      queryClient.invalidateQueries({ queryKey: ["company-jobs", selectedCompanyId] });
      queryClient.invalidateQueries({ queryKey: ["company-ingestion-runs", selectedCompanyId] });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["jobs-feed"] });
      queryClient.invalidateQueries({ queryKey: ["ingestion-runs"] });
      if (run.status === "failed") {
        pushToast({
          title: run.error_message ? `Company scrape failed: ${run.error_message.slice(0, 140)}` : "Company scrape failed",
          tone: "error",
        });
        return;
      }
      if (run.discovered_count === 0) {
        pushToast({ title: "Company scrape completed: 0 jobs found", tone: "info" });
        return;
      }
      pushToast({ title: `Company scrape captured ${run.discovered_count} jobs`, tone: "success" });
    },
    onError: (error) => pushToast({ title: describeApiError(error, "Failed to scrape company jobs"), tone: "error" }),
  });

  const detail = companyDetailQuery.data || null;
  const linkedJobs = linkedJobsQuery.data ?? emptyJobs;
  const companyRuns = companyRunsQuery.data ?? emptyRuns;
  const selectedRole = roles.find((role) => String(role.id) === selectedRoleId) || null;
  const selectedPortal = detail?.portals.find((portal) => String(portal.id) === selectedPortalId) || null;
  const activeCompanyLabel = useMemo(
    () => companies.find((company) => company.id === selectedCompanyId)?.name || "No company selected",
    [companies, selectedCompanyId],
  );

  useEffect(() => {
    if (!detail?.portals.length) {
      setSelectedPortalId("");
      return;
    }
    if (selectedPortalId && detail.portals.some((portal) => String(portal.id) === selectedPortalId)) {
      return;
    }
    setSelectedPortalId("");
  }, [detail?.portals, selectedPortalId]);

  const handleCompanySubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    createCompanyMutation.mutate(companyForm);
  };

  const handlePortalSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedCompanyId) {
      return;
    }
    createPortalMutation.mutate(portalForm);
  };

  const handleContactSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedCompanyId) {
      return;
    }
    createContactMutation.mutate(contactForm);
  };

  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Company Intelligence"
          title="Build your target company directory"
          description="Resolve canonical careers endpoints, preserve recruiter context, and keep future job ingestion tied to reusable company records."
        />

        <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <Card className="space-y-4">
            <div className="space-y-1">
              <h2 className="text-xl font-semibold text-white">Create company</h2>
              <p className="text-sm text-slate-400">User-scoped directory records keep scraping, dedupe, and outreach metadata inspectable.</p>
            </div>
            <form className="space-y-3" onSubmit={handleCompanySubmit}>
              <Input
                placeholder="Company name"
                value={companyForm.name}
                onChange={(event) => setCompanyForm((current) => ({ ...current, name: event.target.value }))}
              />
              <Input
                placeholder="Website URL"
                value={companyForm.website_url}
                onChange={(event) => setCompanyForm((current) => ({ ...current, website_url: event.target.value }))}
              />
              <Input
                placeholder="Careers URL"
                value={companyForm.careers_url}
                onChange={(event) => setCompanyForm((current) => ({ ...current, careers_url: event.target.value }))}
              />
              <Input
                placeholder="LinkedIn URL"
                value={companyForm.linkedin_url}
                onChange={(event) => setCompanyForm((current) => ({ ...current, linkedin_url: event.target.value }))}
              />
              <div className="grid gap-3 lg:grid-cols-2">
                <Input
                  placeholder="HQ location"
                  value={companyForm.hq_location}
                  onChange={(event) => setCompanyForm((current) => ({ ...current, hq_location: event.target.value }))}
                />
                <Input
                  placeholder="Industry"
                  value={companyForm.industry}
                  onChange={(event) => setCompanyForm((current) => ({ ...current, industry: event.target.value }))}
                />
              </div>
              <Textarea
                placeholder="Notes"
                value={companyForm.notes}
                onChange={(event) => setCompanyForm((current) => ({ ...current, notes: event.target.value }))}
              />
              <Button className="w-full" disabled={createCompanyMutation.isPending || companyForm.name.trim().length < 2} type="submit">
                {createCompanyMutation.isPending ? "Saving…" : "Create company"}
              </Button>
            </form>

            <div className="space-y-3">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Directory</h3>
                <Badge>{companies.length} companies</Badge>
              </div>
              {companies.length ? (
                <div className="space-y-2">
                  {companies.map((company) => {
                    const active = company.id === selectedCompanyId;
                    return (
                      <button
                        key={company.id}
                        className={`w-full rounded-2xl border px-4 py-3 text-left transition ${
                          active
                            ? "border-cyan-400/50 bg-cyan-500/10"
                            : "border-white/10 bg-slate-950/60 hover:border-cyan-300/30"
                        } focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950`}
                        onClick={() => setSelectedCompanyId(company.id)}
                        type="button"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <p className="text-sm font-semibold text-white">{company.name}</p>
                            <p className="text-xs text-slate-400">{company.industry || "Industry not set"}</p>
                          </div>
                          <Badge tone={company.active ? "success" : "default"}>
                            {company.active ? "Active" : "Archived"}
                          </Badge>
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <EmptyState title="No companies yet" description="Create your first company record to start building reusable source intelligence." />
              )}
            </div>
          </Card>

          <div className="space-y-4">
            <Card className="space-y-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-xl font-semibold text-white">{activeCompanyLabel}</h2>
                  <p className="text-sm text-slate-400">Canonical company record, careers endpoints, and linked jobs.</p>
                </div>
                {detail ? <Badge>{detail.normalized_name}</Badge> : null}
              </div>
              {detail ? (
                <div className="grid gap-4 lg:grid-cols-3">
                  <div className="space-y-2 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Core profile</p>
                    <p className="text-sm text-white">{detail.website_url || "No website set"}</p>
                    <p className="text-sm text-white">{detail.careers_url || "No careers URL set"}</p>
                    <p className="text-sm text-slate-300">{detail.hq_location || "HQ location not set"}</p>
                    <p className="text-sm text-slate-400">{detail.notes || "No notes yet"}</p>
                  </div>
                  <div className="space-y-2 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Linked jobs</p>
                    <p className="text-3xl font-semibold text-white">{linkedJobs.length}</p>
                    <p className="text-sm text-slate-400">Jobs matched to this company through manual import or role ingestion.</p>
                  </div>
                  <div className="space-y-3 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                    <div className="space-y-1">
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Scrape controls</p>
                      <p className="text-sm text-slate-300">Resolve canonical portals, choose a role policy, and ingest linked jobs.</p>
                    </div>
                    <select
                      className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
                      value={selectedRoleId}
                      onChange={(event) => setSelectedRoleId(event.target.value)}
                    >
                      <option value="">Select role strategy</option>
                      {roles.map((role) => (
                        <option key={role.id} value={role.id}>
                          {role.name}
                        </option>
                      ))}
                    </select>
                    <select
                      className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-100"
                      value={selectedPortalId}
                      onChange={(event) => setSelectedPortalId(event.target.value)}
                    >
                      <option value="">All company portals</option>
                      {detail.portals.map((portal) => (
                        <option key={portal.id} value={portal.id}>
                          {portal.provider_kind} · {portal.board_token || portal.base_url || `Portal #${portal.id}`}
                        </option>
                      ))}
                    </select>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        disabled={!selectedCompanyId || resolvePortalsMutation.isPending}
                        onClick={() => resolvePortalsMutation.mutate()}
                        type="button"
                        variant="secondary"
                      >
                        {resolvePortalsMutation.isPending ? "Resolving…" : "Resolve portals"}
                      </Button>
                      <Button
                        disabled={!selectedCompanyId || !selectedRole || scrapeCompanyMutation.isPending}
                        onClick={() => scrapeCompanyMutation.mutate()}
                        type="button"
                      >
                        {scrapeCompanyMutation.isPending ? "Scraping…" : "Scrape jobs"}
                      </Button>
                    </div>
                    <p className="text-xs text-slate-400">
                      {selectedRole
                        ? `Scoring will use ${selectedRole.name}.`
                        : "Create a role strategy first so discovered jobs can be scored and routed correctly."}
                      {selectedPortal ? ` Scraping is scoped to ${selectedPortal.provider_kind}.` : " Scraping will use every configured portal for this company."}
                    </p>
                  </div>
                </div>
              ) : (
                <EmptyState title="Select a company" description="Pick a company from the directory to inspect portals, contacts, and linked jobs." />
              )}
            </Card>

            <div className="grid gap-4 xl:grid-cols-2">
              <Card className="space-y-4">
                <div className="space-y-1">
                  <h3 className="text-lg font-semibold text-white">Career portals</h3>
                  <p className="text-sm text-slate-400">Attach canonical boards so future scrapers can resolve source identity before creating jobs.</p>
                </div>
                <form className="space-y-3" onSubmit={handlePortalSubmit}>
                  <Input
                    placeholder="Provider kind"
                    value={portalForm.provider_kind}
                    onChange={(event) => setPortalForm((current) => ({ ...current, provider_kind: event.target.value }))}
                  />
                  <Input
                    placeholder="Portal base URL"
                    value={portalForm.base_url}
                    onChange={(event) => setPortalForm((current) => ({ ...current, base_url: event.target.value }))}
                  />
                  <Input
                    placeholder="Board token"
                    value={portalForm.board_token}
                    onChange={(event) => setPortalForm((current) => ({ ...current, board_token: event.target.value }))}
                  />
                  <Textarea
                    placeholder="Notes"
                    value={portalForm.notes}
                    onChange={(event) => setPortalForm((current) => ({ ...current, notes: event.target.value }))}
                  />
                  <Button className="w-full" disabled={!selectedCompanyId || createPortalMutation.isPending} type="submit" variant="secondary">
                    {createPortalMutation.isPending ? "Adding…" : "Add portal"}
                  </Button>
                </form>
                {detail?.portals.length ? (
                  <div className="space-y-3">
                    {detail.portals.map((portal) => (
                      <div key={portal.id} className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold text-white">{portal.provider_kind}</p>
                          <div className="flex flex-wrap items-center gap-2">
                            <Badge>{portal.health_status || "unknown"}</Badge>
                            <Badge tone={portal.supports_structured_fetch ? "success" : "default"}>
                              {portal.supports_structured_fetch ? "Structured" : "Manual"}
                            </Badge>
                          </div>
                        </div>
                        <p className="text-sm text-slate-300">{portal.base_url || "No base URL"}</p>
                        <p className="text-xs text-slate-500">{portal.board_token || "No board token"}</p>
                        <p className="mt-2 text-xs text-slate-400">
                          Last success: {formatTimestamp(portal.last_success_at)} · Last check: {formatTimestamp(portal.last_checked_at)} · Last jobs:{" "}
                          {portal.last_job_count}
                        </p>
                        {portal.last_error ? <p className="mt-2 text-xs text-rose-300">{portal.last_error}</p> : null}
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState title="No portals yet" description="Add a Greenhouse, Lever, or direct careers endpoint." />
                )}
              </Card>

              <Card className="space-y-4">
                <div className="space-y-1">
                  <h3 className="text-lg font-semibold text-white">Contacts</h3>
                  <p className="text-sm text-slate-400">Keep recruiter and HR context separate from job records so it stays reusable across openings.</p>
                </div>
                <form className="space-y-3" onSubmit={handleContactSubmit}>
                  <Input
                    placeholder="Full name"
                    value={contactForm.full_name}
                    onChange={(event) => setContactForm((current) => ({ ...current, full_name: event.target.value }))}
                  />
                  <div className="grid gap-3 lg:grid-cols-2">
                    <Input
                      placeholder="Title"
                      value={contactForm.title}
                      onChange={(event) => setContactForm((current) => ({ ...current, title: event.target.value }))}
                    />
                    <Input
                      placeholder="Email"
                      value={contactForm.email}
                      onChange={(event) => setContactForm((current) => ({ ...current, email: event.target.value }))}
                    />
                  </div>
                  <Input
                    placeholder="LinkedIn URL"
                    value={contactForm.linkedin_url}
                    onChange={(event) => setContactForm((current) => ({ ...current, linkedin_url: event.target.value }))}
                  />
                  <Textarea
                    placeholder="Notes"
                    value={contactForm.notes}
                    onChange={(event) => setContactForm((current) => ({ ...current, notes: event.target.value }))}
                  />
                  <Button className="w-full" disabled={!selectedCompanyId || createContactMutation.isPending || contactForm.full_name.trim().length < 2} type="submit" variant="secondary">
                    {createContactMutation.isPending ? "Adding…" : "Add contact"}
                  </Button>
                </form>
                {detail?.contacts.length ? (
                  <div className="space-y-3">
                    {detail.contacts.map((contact) => (
                      <div key={contact.id} className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold text-white">{contact.full_name}</p>
                          <Badge>{contact.contact_type}</Badge>
                        </div>
                        <p className="text-sm text-slate-300">{contact.title || "Title not set"}</p>
                        <p className="text-xs text-slate-500">{contact.email || "No email captured"}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState title="No contacts yet" description="Add recruiter or HR contacts you want to preserve at the company level." />
                )}
              </Card>
            </div>

            <Card className="space-y-4">
              <div className="space-y-1">
                <h3 className="text-lg font-semibold text-white">Recent company scrape runs</h3>
                <p className="text-sm text-slate-400">Company-scoped ingestion runs keep source identity and role policy attached before jobs land in the board.</p>
              </div>
              {companyRuns.length ? (
                <div className="space-y-3">
                  {companyRuns.slice(0, 6).map((run) => (
                    <div key={run.id} className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold text-white">
                            {run.trigger_kind === "company_portal_scrape" ? "Portal scrape" : "Company scrape"}
                          </p>
                          <p className="text-xs text-slate-400">
                            Role #{run.role_id}
                            {run.company_portal_id ? ` · Portal #${run.company_portal_id}` : " · All portals"}
                          </p>
                        </div>
                        <Badge>{run.status}</Badge>
                      </div>
                      <p className="mt-2 text-sm text-slate-300">
                        {run.discovered_count} discovered · {run.inserted_count} inserted · {run.updated_count} updated · {run.failed_count} failed
                      </p>
                      <p className="text-xs text-slate-400">
                        Started {formatTimestamp(run.started_at)}{run.finished_at ? ` · Finished ${formatTimestamp(run.finished_at)}` : ""}
                      </p>
                      {run.error_message ? <p className="mt-2 text-sm text-rose-300">{run.error_message}</p> : null}
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState title="No company scrape runs yet" description="Resolve portals and run the first company scrape from this page." />
              )}
            </Card>

            <Card className="space-y-4">
              <div className="space-y-1">
                <h3 className="text-lg font-semibold text-white">Linked jobs</h3>
                <p className="text-sm text-slate-400">Jobs already resolved to this company through the directory matcher.</p>
              </div>
              {linkedJobs.length ? (
                <div className="grid gap-3 lg:grid-cols-2">
                  {linkedJobs.slice(0, 6).map((job) => (
                    <div key={job.id} className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold text-white">{job.title}</p>
                        {job.latest_score ? <Badge tone="success">{Math.round(job.latest_score)} match</Badge> : null}
                      </div>
                      <p className="text-sm text-slate-300">{job.location || "Location not provided"}</p>
                      <p className="text-xs text-slate-500">{job.source}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState title="No linked jobs yet" description="Manual jobs and role-ingested jobs will show up here when their company matches the directory." />
              )}
            </Card>
          </div>
        </div>
      </section>
    </ProtectedPage>
  );
}
