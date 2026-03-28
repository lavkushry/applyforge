export type SessionUser = {
  id: number;
  email: string;
};

export type CandidateBasics = {
  full_name: string;
  headline: string;
  email?: string | null;
  phone: string;
  location: string;
  target_role: string;
  preferred_locations: string[];
};

export type CandidateProfile = {
  id: number;
  user_id: number;
  basics: CandidateBasics;
  summary: string;
  skills: string[];
  experience: Array<Record<string, unknown>>;
  projects: Array<Record<string, unknown>>;
  education: Array<Record<string, unknown>>;
  certifications: Array<Record<string, unknown>>;
  links: Array<{ label: string; url: string }>;
  preferences: Record<string, unknown>;
  saved_answers: Record<string, unknown>;
  fact_locked: boolean;
};

export type Job = {
  id: number;
  user_id: number;
  company_id: number | null;
  role_id: number | null;
  title: string;
  company: string;
  location: string;
  remote_type: string;
  salary: string;
  source: string;
  application_url: string;
  description: string;
  normalized_description: Record<string, unknown>;
  seniority: string;
  employment_type: string;
  visa_support: string;
  tags: string[];
  stack_tags: string[];
  domain_tags: string[];
  source_metadata: Record<string, unknown>;
  enrichment_status: string;
  enrichment_error: string;
  enrichment_metadata: Record<string, unknown>;
  enrichment_revision: number;
  source_document_file_id: number | null;
  latest_score: number;
  latest_score_revision: number;
  latest_recommendation: string;
  last_scored_at: string | null;
  first_seen_at: string;
  last_seen_at: string;
  expired_at: string | null;
  active: boolean;
  dedupe_key: string;
  created_at: string;
};

export type JobScore = {
  id: number;
  job_id: number;
  role_id: number | null;
  enrichment_revision: number;
  overall_score: number;
  score_breakdown: Record<string, number>;
  missing_skills: string[];
  strengths: string[];
  reasons: string[];
  recommendation: string;
  created_at: string;
};

export type ResumeVersion = {
  id: number;
  resume_id: number;
  job_id: number | null;
  theme_id: number | null;
  title: string;
  variant: string;
  theme_variant: string;
  ats_mode: boolean;
  content_json: Record<string, unknown>;
  diff_metadata: Record<string, unknown>;
  export_status: string;
  pdf_file_id: number | null;
  created_at: string;
};

export type ResumeTheme = {
  id: number;
  slug: string;
  label: string;
  description: string;
  accent_color: string;
  layout_mode: string;
  is_ats_safe: boolean;
  metadata_json: Record<string, unknown>;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type ResumePreview = {
  theme: ResumeTheme;
  blocks: Array<{ title: string; lines: string[] }>;
};

export type ResumeTemplateSection = {
  key: string;
  label: string;
  description: string;
  repeatable: boolean;
  required: boolean;
  placeholder: string;
};

export type ResumeTemplate = {
  key: string;
  label: string;
  description: string;
  format: string;
  asset_name: string;
  recommended_theme_slugs: string[];
  section_keys: string[];
};

export type ResumeTemplateCatalog = {
  templates: ResumeTemplate[];
  sections: ResumeTemplateSection[];
};

export type ResumeTemplateRender = {
  template: ResumeTemplate;
  rendered_content: string;
  sections: ResumeTemplateSection[];
};

export type TargetRoleSource = {
  id: number;
  role_id: number;
  kind: string;
  label: string;
  base_url: string;
  config: Record<string, unknown>;
  enabled: boolean;
  last_checked_at: string | null;
  created_at: string;
  updated_at: string;
};

export type TargetRole = {
  id: number;
  user_id: number;
  name: string;
  aliases: string[];
  keywords: string[];
  preferred_locations: string[];
  remote_preference: string;
  salary_target: string;
  visa_preference: string;
  seniority: string;
  companies_include: string[];
  companies_exclude: string[];
  scrape_cadence_minutes: number;
  automation_enabled: boolean;
  min_auto_apply_score: number;
  active: boolean;
  sources: TargetRoleSource[];
  created_at: string;
  updated_at: string;
};

export type DiscoverySourcePreset = {
  key: string;
  label: string;
  kind: string;
  base_url: string;
  config: Record<string, unknown>;
  notes: string;
  tags: string[];
};

export type DiscoverySearchTemplate = {
  key: string;
  label: string;
  role_name: string;
  aliases: string[];
  keywords: string[];
  preferred_locations: string[];
  remote_preference: string;
  seniority: string;
  source_preset_keys: string[];
};

export type DiscoveryPresetCatalog = {
  source_presets: DiscoverySourcePreset[];
  search_templates: DiscoverySearchTemplate[];
  blocked_domains: string[];
};

export type Company = {
  id: number;
  user_id: number;
  name: string;
  normalized_name: string;
  website_url: string;
  careers_url: string;
  linkedin_url: string;
  hq_location: string;
  industry: string;
  notes: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type CompanyPortal = {
  id: number;
  company_id: number;
  provider_kind: string;
  base_url: string;
  board_token: string;
  health_status: string;
  supports_structured_fetch: boolean;
  last_checked_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type CompanyContact = {
  id: number;
  company_id: number;
  full_name: string;
  title: string;
  email: string;
  linkedin_url: string;
  contact_type: string;
  source: string;
  source_url: string;
  confidence: number;
  last_verified_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type CompanyDetail = Company & {
  portals: CompanyPortal[];
  contacts: CompanyContact[];
};

export type JobFeedEvent = {
  id: number;
  role_id: number;
  role_name: string;
  job_id: number;
  run_id: number | null;
  event_type: string;
  event_metadata: Record<string, unknown>;
  created_at: string;
  job: Job | null;
};

export type IngestionRun = {
  id: number;
  role_id: number;
  role_name?: string;
  status: string;
  source_count: number;
  discovered_count: number;
  inserted_count: number;
  updated_count: number;
  enriched_count: number;
  failed_count: number;
  expired_count: number;
  error_message: string;
  started_at: string;
  finished_at: string | null;
};

export type InboxConnection = {
  id: number;
  user_id: number;
  provider: string;
  email: string;
  status: string;
  scopes: string[];
  token_masked: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type InboxOAuthProvider = {
  provider: string;
  configured: boolean;
  authorization_enabled: boolean;
  redirect_uri: string;
  scopes: string[];
  required_env: string[];
  missing_env: string[];
};

export type InboxOtpEvent = {
  id: number;
  connection_id: number;
  run_id: number | null;
  status: string;
  sender: string;
  subject_masked: string;
  code_last4: string;
  error_message: string;
  created_at: string;
};

export type CoverLetter = {
  id: number;
  job_id: number;
  content: string;
  tone: string;
  created_at: string;
};

export type Application = {
  id: number;
  user_id: number;
  job_id: number;
  status: string;
  notes: string;
  latest_run_id: number | null;
  created_at: string;
  job?: {
    id: number;
    title: string;
    company: string;
    application_url: string;
    latest_score: number;
    latest_recommendation: string;
    enrichment_status: string;
    enrichment_revision: number;
  } | null;
  latest_run?: {
    id: number;
    mode: string;
    status: string;
    current_step: string;
  } | null;
  action_required?: {
    name: string;
    step_kind: string;
    reason: string;
  } | null;
  pipeline?: {
    discovered: boolean;
    enriched: boolean;
    scored: boolean;
    tailored: boolean;
    cover_letter: boolean;
    packet_ready: boolean;
    auto_ready: boolean;
  };
  packet_summary?: ApplicationPacket | null;
};

export type ApplicationRun = {
  id: number;
  application_id: number;
  role_id: number | null;
  mode: string;
  status: string;
  current_step: string;
  external_task_id: string;
  error_message: string;
  policy_snapshot: Record<string, unknown>;
  started_at: string;
  finished_at: string | null;
};

export type ApplicationPacket = {
  ready: boolean;
  auto_submit_allowed: boolean;
  resume_file_id: number | null;
  cover_letter_id: number | null;
  upload_ready: boolean;
  missing_answers: string[];
  risk_summary: string[];
  blocking_issues: string[];
  auto_policy_reasons: string[];
  answer_provenance: Record<string, string>;
  answer_keys: string[];
};

export type ApplicationPrepareResponse = {
  application: Application;
  packet: ApplicationPacket;
};

export type ApplicationStep = {
  id: number;
  run_id: number;
  name: string;
  status: string;
  step_kind: string;
  requires_approval: boolean;
  screenshot_file_id: number | null;
  output: Record<string, unknown>;
  masked_output: Record<string, unknown>;
  retry_count: number;
  started_at: string;
  completed_at: string | null;
};

export type RunDetail = {
  run: ApplicationRun;
  steps: ApplicationStep[];
};

export type ApplicationsDashboard = {
  status_counts: Record<string, number>;
  run_counts: Record<string, number>;
  pipeline_counts: Record<string, number>;
};

export type HealthStatus = {
  status: string;
  database: string;
  redis: string;
  timestamp: string;
};

export type AdminRun = {
  id: number;
  application_id: number;
  job_id: number;
  mode: string;
  status: string;
  current_step: string;
  error_message: string;
  external_task_id: string;
  started_at: string;
  finished_at: string | null;
};

export type AdminStepError = {
  id: number;
  run_id: number;
  application_id: number;
  job_id: number;
  name: string;
  step_kind: string;
  status: string;
  requires_approval: boolean;
  output: Record<string, unknown>;
};

export type AdminEnrichmentError = {
  job_id: number;
  role_id: number;
  role_name: string;
  title: string;
  company: string;
  application_url: string;
  error_message: string;
  source_kind: string;
  source_url: string;
  updated_at: string;
};

export type WizardStep = {
  key: string;
  title: string;
  description: string;
  status: string;
  href: string;
};

export type WizardSummary = {
  profile_ready: boolean;
  resume_ready: boolean;
  inbox_ready: boolean;
  role_count: number;
  job_count: number;
  tailored_resume_count: number;
  steps: WizardStep[];
  recommended_templates: DiscoverySearchTemplate[];
  blocked_domains: string[];
};
