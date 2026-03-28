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
import { api } from "@/lib/api";
import type { Company, CompanyContact, CompanyDetail, CompanyPortal, Job } from "@/lib/types";
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

export default function CompaniesPage() {
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
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

  useEffect(() => {
    if (!companies.length) {
      setSelectedCompanyId(null);
      return;
    }
    if (!selectedCompanyId || !companies.some((company) => company.id === selectedCompanyId)) {
      setSelectedCompanyId(companies[0].id);
    }
  }, [companies, selectedCompanyId]);

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
    mutationFn: (payload: typeof emptyPortal) =>
      api<CompanyPortal>(`/companies/${selectedCompanyId}/portals`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["company", selectedCompanyId] });
      setPortalForm(emptyPortal);
      pushToast({ title: "Company portal added", tone: "success" });
    },
    onError: () => pushToast({ title: "Failed to add portal", tone: "error" }),
  });

  const createContactMutation = useMutation({
    mutationFn: (payload: typeof emptyContact) =>
      api<CompanyContact>(`/companies/${selectedCompanyId}/contacts`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["company", selectedCompanyId] });
      setContactForm(emptyContact);
      pushToast({ title: "Company contact added", tone: "success" });
    },
    onError: () => pushToast({ title: "Failed to add contact", tone: "error" }),
  });

  const detail = companyDetailQuery.data || null;
  const linkedJobs = linkedJobsQuery.data ?? emptyJobs;
  const activeCompanyLabel = useMemo(
    () => companies.find((company) => company.id === selectedCompanyId)?.name || "No company selected",
    [companies, selectedCompanyId],
  );

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
                        }`}
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
                <div className="grid gap-4 lg:grid-cols-2">
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
                          <Badge tone={portal.supports_structured_fetch ? "success" : "default"}>
                            {portal.supports_structured_fetch ? "Structured" : "Manual"}
                          </Badge>
                        </div>
                        <p className="text-sm text-slate-300">{portal.base_url || "No base URL"}</p>
                        <p className="text-xs text-slate-500">{portal.board_token || "No board token"}</p>
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
