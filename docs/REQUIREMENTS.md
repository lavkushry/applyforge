# ApplyForge Product Requirements

## Overview

ApplyForge is a job hunt operating system for serious applicants who want one workflow for:

1. importing and structuring a master resume,
2. discovering and ranking jobs in near real time,
3. generating a role-matched resume and cover letter,
4. preparing and running guarded application automation,
5. tracking status, evidence, and follow-up actions.

This document clarifies the next product expansion requested for ApplyForge:

- selectable light, ATS-friendly resume themes inspired by RenderCV-style structured templates,
- realtime role-based job scraping and feed delivery,
- stronger job-to-resume tailoring,
- ApplyPilot-style step-based application automation,
- permissioned inbox and OTP retrieval for supported application flows.

## Current Implementation Snapshot

The current repository already includes the following product capabilities:

- canonical candidate profile with fact-locked tailoring constraints,
- role registry with scrape preferences and automation thresholds,
- near-realtime role feed backed by ingestion runs and feed events,
- three ATS-safe light resume themes with preview and export metadata,
- RenderCV-compatible structured resume input generation with internal PDF fallback,
- application runs with per-step status, pause gates, masked outputs, and diagnostics,
- inbox integrations for Gmail and Outlook with encrypted token storage,
- OAuth start and callback routes plus provider-readiness reporting for inbox setup.

This means future work should build on these contracts instead of reintroducing parallel flows.

## Product Clarifications

The following points are fixed requirements, not optional interpretations:

1. ApplyForge may optimize for ATS readability and role relevance, but it shall not promise a 100% interview or selection rate.
2. ApplyForge shall not invent resume facts, legal answers, salary history, notice periods, work authorization, or any unknown user data.
3. ApplyForge shall not remove safety-critical prompt guardrails for truthfulness, risk detection, approval routing, or audit logging.
4. ApplyForge may support inbox access for OTP retrieval only with explicit user consent, scoped credentials, audit logs, and a manual fallback.
5. ApplyForge shall not attempt to bypass CAPTCHAs, anti-bot challenges, or employer security controls.

## Primary User Value

- A user uploads one source resume and maintains one canonical profile.
- A user subscribes to one or more target roles and sees a live feed of matching jobs.
- A user chooses which roles or companies should be eligible for automation.
- A user can generate a tailored resume in a clean, highly readable, ATS-friendly light theme.
- A user can run draft, assisted, or approved auto-apply workflows with evidence and pause points.

## Users

1. Individual job seekers applying repeatedly for a focused set of roles.
2. Power users managing multiple resume strategies for different role families.
3. Career coaches or agencies managing candidates in later phases.
4. Internal operators reviewing automation failures and prompt traces.

## Functional Requirements

### 1. Resume Templates and Export

1. Where a user has uploaded or created a canonical profile, the system shall offer multiple light, ATS-friendly resume themes.
2. When a user selects a resume theme, the system shall preview the selected theme before export.
3. The system shall provide at least three built-in resume themes:
   - Classic ATS Light
   - Modern Minimal Light
   - Compact Technical Light
4. The system shall store the selected theme per resume version and per tailored resume export.
5. When a resume is exported, the system shall generate a machine-readable PDF with selectable text and no image-only content.
6. Where a template contains multi-column or decorative elements, the system shall enforce ATS-safe constraints or reject that template for ATS mode.
7. When a user requests an ATS export, the system shall use a single-column or ATS-safe layout with high text extractability.
8. The system shall preserve a structured intermediate resume representation so export engines can be swapped later between internal rendering, HTML-to-PDF, or a RenderCV-compatible adapter.
9. Where RenderCV is unavailable or fails at runtime, the system shall preserve export continuity with a safe internal fallback renderer and log the renderer failure for diagnostics.

### 2. Resume Upload and Canonical Profile

1. When a user uploads a PDF, DOCX, or TXT resume, the system shall extract text and parse it into structured profile sections.
2. If parsing confidence is low for any section, the system shall mark that section as review required.
3. The system shall keep the canonical candidate profile as the only trusted source of factual resume content.
4. When a user edits profile data, the system shall persist section-level versioned updates.
5. The system shall support multiple target role strategies while keeping one fact-locked master profile.

### 3. Role Registry and Automation Preferences

1. The system shall allow a user to define one or more target roles for discovery and automation.
2. Each target role shall store:
   - role name,
   - aliases and keywords,
   - preferred locations,
   - remote preference,
   - salary preference,
   - visa preference,
   - seniority range,
   - companies to prioritize or avoid,
   - automation enabled state,
   - scrape cadence.
3. When a target role is active, the system shall use that role definition to drive job scraping, ranking, and eligibility for automation.
4. The system shall keep a table of role requirements and matching heuristics so each job can be scored against the intended role profile.
5. The role registry shall remain the controlling source for scrape cadence, automation thresholds, and future multi-role strategy support.

### 4. Realtime Job Scraper Engine

1. When a target role is active, the system shall scrape or ingest jobs on a schedule for that role.
2. The system shall normalize all ingested jobs into a single schema before scoring or display.
3. The system shall deduplicate jobs across sources using application URL, normalized company and title, and content fingerprints.
4. The system shall record when a job was first seen, last seen, source, scrape run, and freshness status.
5. The system shall expose a near-realtime jobs feed ordered by recency and score.
6. When a job feed item is clicked, the system shall show the source link, normalized details, and automation eligibility.
7. If a job disappears or expires, the system shall preserve the record and mark it inactive rather than deleting it.
8. The system shall support manual import by URL or pasted description alongside scheduled scraping.
9. ATS-first sources shall remain the default ingestion scope for the MVP, with Greenhouse, Lever, and predictable direct career pages prioritized over broad consumer job boards.

### 5. Job Matching and Tailoring

1. When a new job is ingested for a role, the system shall score it against both the canonical candidate profile and the selected role strategy.
2. The scoring output shall include:
   - overall score,
   - role-match score,
   - skills overlap,
   - missing must-haves,
   - nice-to-have overlap,
   - seniority fit,
   - location fit,
   - compensation fit if available,
   - recommendation.
3. When a user tailors a resume for a job, the system shall only reorder, emphasize, summarize, or select existing factual content.
4. The system shall create a tailored summary targeted to the job description without introducing unverifiable claims.
5. The system shall rank and reorder skills and bullets based on role and job relevance.
6. If a job requires a missing qualification, the system shall highlight the gap instead of fabricating coverage.
7. The system shall persist each tailored resume version, diff metadata, selected theme, and linked job.
8. Where a job score is below a user-defined threshold, the system shall default automation eligibility to off.

### 6. Application Automation

1. The system shall support draft mode, assisted mode, and approved auto mode.
2. When a user runs draft mode, the system shall prepare answers, files, and warnings without launching a browser.
3. When a user runs assisted mode, the system shall open the application flow, fill supported fields, and pause before final submission.
4. Where approved auto mode is enabled, the system shall only auto-submit jobs that satisfy the user’s automation policy and risk thresholds.
5. Every automation run shall persist:
   - run status,
   - mode,
   - timestamps,
   - per-step logs,
   - retry count,
   - screenshots,
   - structured step outputs,
   - final disposition.
6. If an application contains risky, legal, compensation, or ambiguous questions, the system shall pause for explicit user approval.
7. If an application requires unsupported controls or anti-bot validation, the system shall fail gracefully and hand control back to the user.
8. The system shall attach the correct tailored resume variant for the active job and role.
9. OTP retrieval and approval pauses shall be represented as first-class steps in the run timeline so runs remain inspectable after partial automation.

### 7. Inbox and OTP Access

1. The system shall support a user-authorized inbox connection for reading application-related OTPs and verification emails.
2. The system shall limit OTP retrieval to configured providers and scoped mailbox access where possible.
3. When an OTP is requested during an application run, the system shall search recent inbox messages for matching sender, subject, or code patterns.
4. The system shall mask OTP values in logs and screenshots.
5. If OTP retrieval confidence is low, the system shall pause and require manual confirmation.
6. The system shall store inbox credentials or tokens only through encrypted, environment-backed or secret-managed storage paths.
7. The system shall allow a user to disable inbox access entirely and continue with manual OTP entry.
8. Gmail and Outlook OAuth connections shall expose setup readiness, redirect URIs, and missing environment variables so operator setup can be diagnosed without reading source code.

### 8. Diagnostics and Admin

1. The system shall expose scrape-run status, job ingestion failures, prompt traces, automation failures, and screenshot artifacts in an internal diagnostics panel.
2. The system shall preserve audit records for prompt usage, automation approvals, OTP retrieval attempts, and resume exports.
3. When a scrape or apply run fails, the system shall expose a retry action with the failure reason and the last successful checkpoint.

## Non-Functional Requirements

### Reliability

1. The system shall use idempotent ingestion and automation checkpoints where possible.
2. The system shall support resuming failed runs from the last safe checkpoint.
3. The system shall tolerate partial failures in scraping, parsing, PDF export, and browser automation without corrupting user data.

### Performance

1. The dashboard feed shall load the latest job events within 2 seconds for normal local-development datasets.
2. Tailored resume generation shall complete within 10 seconds for standard job descriptions under normal conditions.
3. OTP lookup shall return a result or a manual fallback prompt within 15 seconds.

### Security

1. All auth, inbox, and automation-sensitive actions shall require authenticated user context.
2. The system shall encrypt or otherwise protect sensitive integration secrets at rest.
3. The system shall mask secrets, tokens, OTP codes, and sensitive prompt fragments in logs.
4. The system shall not disable approval routing for risky answers.

### Observability

1. The system shall emit structured logs for scrape runs, score generation, tailoring, export, and application automation.
2. The system shall preserve prompt metadata and model routing information without storing raw secrets.
3. The system shall support diagnostics on per-job, per-role, and per-run basis.

## Product Invariants For Future Changes

1. The canonical candidate profile stays authoritative over every generated or tailored document.
2. Tailoring, cover-letter generation, and question answering may optimize phrasing, but they may not introduce unsupported facts.
3. Resume templates are a presentation concern; they must not become the source of truth for user data.
4. Role strategy drives discovery and automation policy; job-specific overrides are secondary.
5. Application automation must always leave an audit trail with enough evidence to understand what happened.
6. Inbox access exists only to help the candidate complete their own flow, not to expand surveillance or scrape unrelated mail.

## Context Notes For Future Implementers

1. If you add new job sources, keep dedupe and freshness semantics compatible with the existing role feed.
2. If you add a new renderer, preserve the normalized resume document shape used by the current theme/export flow.
3. If you change application execution behavior, keep `application_runs` and `application_steps` durable and human-readable.
4. If you add richer OAuth support, preserve encrypted token storage and sanitized API responses.
5. If you add AI model usage, prefer deterministic logic first and log masked prompt metadata.

## Acceptance Criteria

1. Given a user uploads a resume, when parsing finishes, then the user can review a structured profile and see any low-confidence fields flagged for edit.
2. Given a user has multiple resume themes, when they open a tailored resume, then they can switch theme and export an ATS-friendly PDF preview.
3. Given a user creates a target role, when scraping runs, then new normalized jobs appear in a feed tagged to that role and sorted by freshness.
4. Given the same job is discovered from two sources, when ingestion completes, then only one job record remains active and both source references are retained.
5. Given a job has required skills the user does not have, when tailoring runs, then the tailored resume highlights relevant experience but does not fabricate missing skills.
6. Given assisted mode is started, when the application reaches submit, then the run pauses and shows screenshots, filled values, and warnings for review.
7. Given an application asks a risky or ambiguous question, when answer generation runs, then the system marks the step as approval required instead of auto-answering.
8. Given inbox access is enabled, when an OTP email arrives during an application run, then the system can retrieve the candidate code, mask it in logs, and continue only after policy allows it.
9. Given OTP retrieval fails or confidence is low, when the timeout expires, then the system pauses and requests manual input without losing the run state.
10. Given a job is no longer available, when the feed refreshes, then the job is marked inactive or expired and previous automation records remain visible.

## Error Handling

| Scenario | System behavior | User-facing response |
|---|---|---|
| Resume parsing fails | Preserve upload, create parse-failed event, allow manual profile creation | `We couldn't fully parse this resume. Review the extracted text or enter sections manually.` |
| Resume theme render fails | Keep tailored content, fallback to default ATS theme, log renderer failure | `This template failed to render. We switched to the default ATS template.` |
| Source site rate limit | Back off scrape worker, mark run partial, retry later | `This source is temporarily rate-limited. We'll retry automatically.` |
| Duplicate job ingestion | Merge source metadata, do not create duplicate visible job | `This job already exists in your feed. Source metadata was updated.` |
| Tailoring detects missing must-have | Highlight gap, lower automation eligibility | `This job has missing required qualifications. Review before applying.` |
| Unsupported application field | Pause run and capture evidence | `This application contains an unsupported step. Review is required.` |
| CAPTCHA or anti-bot challenge | Stop automation and require manual completion | `Automation paused because the site requires human verification.` |
| OTP email not found | Pause run, preserve browser state where possible | `We couldn't retrieve the verification code. Enter it manually to continue.` |
| Inbox token invalid | Disconnect integration, mark run blocked | `Your inbox connection needs to be re-authorized.` |
| Submit confirmation not detected | Mark run uncertain and require user review | `The application may not have been submitted. Please verify the final page.` |

## Implementation Checklist

### Phase A: Resume Themes and Structured Export

1. Add resume theme catalog, selection UI, preview endpoint, and export metadata.
2. Add ATS-safe theme validation rules.
3. Add a RenderCV-compatible adapter or equivalent structured renderer.

### Phase B: Role-Based Discovery and Feed

1. Add target-role models, scrape subscriptions, scrape runs, and feed events.
2. Add scheduled ingestion worker and source adapters.
3. Add realtime or near-realtime feed delivery in the web app.

### Phase C: Stronger Tailoring

1. Add role strategy inputs to the scoring engine.
2. Add per-job tailored resume diffs and theme-aware export.
3. Add stricter missing-skill and risky-answer surfacing in UI.

### Phase D: Apply Automation

1. Expand step engine for field adapters, navigation patterns, and checkpoints.
2. Wire API-to-worker dispatch through Celery or equivalent queue execution.
3. Persist screenshots and artifacts as uploaded file records.

### Phase E: Inbox and OTP Integration

1. Add inbox connection model and provider abstraction.
2. Add OTP retrieval worker step with masking and approval fallback.
3. Add diagnostics, consent copy, and revoke-access controls.

## Explicitly Rejected Requirements

The following requests are not valid product requirements and shall not be implemented:

1. Remove truth, approval, or safety guardrails from prompt generation.
2. Guarantee a 100% resume selection or interview success rate.
3. Fabricate qualifications or answers to increase application conversion.
4. Bypass employer anti-bot controls, CAPTCHAs, or verification systems.
