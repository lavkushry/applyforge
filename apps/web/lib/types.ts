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
  dedupe_key: string;
  created_at: string;
};

export type JobScore = {
  id: number;
  job_id: number;
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
  title: string;
  variant: string;
  content_json: Record<string, unknown>;
  pdf_file_id: number | null;
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
  } | null;
};

export type ApplicationRun = {
  id: number;
  application_id: number;
  mode: string;
  status: string;
  current_step: string;
  external_task_id: string;
  error_message: string;
  started_at: string;
  finished_at: string | null;
};

export type ApplicationStep = {
  id: number;
  run_id: number;
  name: string;
  status: string;
  screenshot_file_id: number | null;
  output: Record<string, unknown>;
  retry_count: number;
  started_at: string;
  completed_at: string | null;
};

export type RunDetail = {
  run: ApplicationRun;
  steps: ApplicationStep[];
};

export type HealthStatus = {
  status: string;
  database: string;
  redis: string;
  timestamp: string;
};
