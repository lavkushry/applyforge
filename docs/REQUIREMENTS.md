# ApplyForge Product Requirements

## 📖 Overview

ApplyForge is an advanced, AI-powered job hunt operating system built for serious applicants. It consolidates multiple fragmented workflows into a single, unified pipeline:

1. **Importing and structuring** a master candidate profile.
2. **Discovering and ranking** job opportunities in near real-time.
3. **Generating** role-matched, highly tailored resumes and cover letters.
4. **Executing** guarded, browser-assisted application automation.
5. **Tracking** application statuses, operational evidence, and necessary follow-up actions.

This document serves as the definitive guide to the current product capabilities, architectural invariants, and the explicit boundaries of what ApplyForge will and will not do.

---

## 🏗️ Current Implementation Snapshot

The ApplyForge repository is currently highly functional and supports the following capabilities out-of-the-box:

- **Identity Management:** A canonical candidate profile architecture enforcing fact-locked tailoring constraints.
- **Discovery Engine:** A robust role registry featuring scrape preferences, automation thresholds, and a near real-time feed powered by background ingestion events.
- **Corporate Intelligence:** User-scoped company directory records integrating canonical career portals and recruiter contacts.
- **Document Generation:**
  - Three ATS-safe light resume themes equipped with preview capabilities and structured export metadata.
  - Packaged Markdown and LaTeX starter templates.
  - A RenderCV-compatible structured input generator featuring a reliable internal PDF fallback renderer.
- **Automation Pipeline:**
  - Exportable user-preference profiles aggregating settings, role strategies, and saved answers.
  - Formalized application packets governing run-state transitions.
  - Durable application runs featuring step-by-step logging, pause gates, masked outputs, and comprehensive diagnostics.
- **Integrations:**
  - OAuth setup readiness (start/callback routes) and provider-status reporting.
  - Secured inbox integrations (Gmail, Outlook) with encrypted token storage for dynamic OTP retrieval.

*Future development must build upon these established contracts rather than introducing redundant or parallel flows.*

---

## 🛑 Strict Product Clarifications

The following directives are fixed constraints, not optional guidelines:

1. **No False Promises:** While ApplyForge optimizes for ATS readability and role relevance, it shall *never* guarantee a 100% interview or selection rate.
2. **Zero Hallucination Tolerance:** ApplyForge shall *never* invent resume facts, legal answers, salary histories, notice periods, work authorizations, or any other unknown user data.
3. **Guardrails Remain Intact:** ApplyForge shall *never* remove safety-critical prompt guardrails governing truthfulness, risk detection, approval routing, or audit logging.
4. **Explicit Consent for Inbox Access:** Inbox access for OTP retrieval is strictly opt-in, requiring explicit user consent, heavily scoped credentials, detailed audit logging, and the constant availability of a manual fallback option.
5. **Respect for Employer Security:** ApplyForge shall *never* attempt to maliciously bypass CAPTCHAs, anti-bot challenges, or standard employer security controls.
6. **Data Privacy:** Company intelligence data remains strictly user-scoped unless a formalized shared-directory architecture is explicitly implemented in the future.

---

## 🎯 Primary User Value Proposition

- **Single Source of Truth:** Users upload one source resume and maintain a single, canonical profile.
- **Targeted Opportunities:** Users subscribe to specific target roles and receive a live feed of highly matched jobs.
- **Granular Control:** Users dictate exactly which roles or companies are eligible for automated applications.
- **Professional Output:** Users generate flawlessly tailored resumes formatted in clean, highly readable, ATS-friendly light themes.
- **Confident Execution:** Users execute draft, assisted, or approved auto-apply workflows backed by irrefutable visual evidence and strict pause points.

---

## 👥 Target Audience

1. **Individual Job Seekers:** Professionals applying repeatedly to a focused set of roles.
2. **Power Users:** Individuals managing complex, multi-strategy resume approaches across disparate role families.
3. **Career Coaches & Agencies:** Professionals managing application pipelines for multiple candidates.
4. **Internal Operators:** Engineers and administrators reviewing automation failures and prompt execution traces.

---

## ⚙️ Functional Requirements

### 1. Resume Templates and Export
1. The system shall offer multiple light, highly ATS-friendly resume themes leveraging the canonical profile.
2. The system shall provide immediate, high-fidelity visual previews before PDF export.
3. The system shall include at least three core themes: *Classic ATS Light*, *Modern Minimal Light*, and *Compact Technical Light*.
4. Theme selections must be persistently stored per resume version and per tailored export.
5. Generated PDFs must be machine-readable, containing selectable text, and completely devoid of image-only text representations.
6. Multi-column or overly decorative templates must either enforce ATS-safe fallback constraints or be rejected entirely when ATS-mode is required.
7. The system shall maintain a structured intermediate representation of the resume, allowing the rendering engine (RenderCV, internal fallback, HTML-to-PDF) to be seamlessly swapped.
8. If RenderCV fails at runtime, the system shall seamlessly default to the internal fallback renderer to guarantee export continuity, while logging the failure for operator review.

### 2. Canonical Profile Management
1. The system shall support PDF, DOCX, and TXT uploads, extracting and structuring data into granular profile sections.
2. Low-confidence parsing extractions must be explicitly flagged to require mandatory user review.
3. The canonical `candidate_profiles` table remains the sole, trusted source for factual resume generation.
4. All user edits to profile data shall be persisted via section-level versioned updates.
5. The system shall seamlessly support multiple target role strategies while relying on a single, fact-locked master profile.

### 3. Role Registry and Preferences
1. Users shall be able to define robust target roles dictating discovery and automation policies.
2. Target roles shall capture: Aliases/keywords, location/remote preferences, salary targets, visa requirements, seniority ranges, company block/allow lists, automation thresholds, and scraping cadences.
3. The active target role strategy must drive all downstream job scraping, ranking algorithms, and auto-apply eligibility flags.
4. The system shall maintain a heuristic table mapping role requirements to enable precise job scoring against the canonical profile.

### 4. Realtime Job Discovery Engine
1. The system shall systematically scrape/ingest jobs based on the active target role schedules.
2. All ingested jobs must be aggressively normalized into a unified schema prior to scoring or display.
3. The system shall execute strict deduplication using application URLs, normalized company names/titles, and content-hashing fingerprints.
4. Job records must durably track provenance: first seen, last seen, source origin, scrape run ID, and freshness state.
5. The UI shall present a near real-time feed, filterable by recency and algorithmic score.
6. The system shall preserve expired or missing jobs by marking them inactive, ensuring historical automation records are never orphaned.
7. Manual job ingestion (via URL or pasted description) must be fully supported alongside scheduled scraping.

### 4A. Company Intelligence Directory
1. The system shall maintain a user-scoped company directory tracking canonical corporate identities.
2. Company records shall store: Normalized names, URLs (website, careers, LinkedIn), HQ location, industry categorization, and active status.
3. The system shall support tracking multiple career portals per company (including ATS provider type and structural fetch capabilities).
4. Newly ingested jobs must heuristically attempt resolution to a canonical company record before settling as an unlinked free-text string.
5. The UI must expose linked jobs within the company directory to allow users to review source quality and deduplication behavior.

### 5. Job Matching and Tailoring
1. Ingested jobs shall be rigorously scored against both the canonical profile and the active target role strategy.
2. Scoring outputs must detail: Overall score, role-match score, skills overlap, critical missing must-haves, seniority/location fit, and a final actionable recommendation.
3. Tailoring algorithms are restricted to reordering, emphasizing, or summarizing existing factual content; introducing unverifiable claims is strictly prohibited.
4. Tailored outputs must explicitly highlight missing qualifications rather than fabricating coverage.
5. The system shall durably persist every tailored resume version, its diff metadata, the selected theme, and its linkage to the target job.
6. Jobs scoring below a user-defined threshold shall have their automation eligibility automatically disabled.

### 6. Application Automation
1. The system shall fully support three execution modes: *Draft* (offline prep), *Assisted* (browser execution with submit pause), and *Approved Auto* (full execution).
2. All automation runs must durably persist: FSM run status, execution mode, timestamps, per-step logs, retry counts, visual screenshots, structured outputs, and final disposition.
3. Applications containing risky, legal, compensation, or ambiguous questions must immediately trigger a manual user approval pause.
4. Applications presenting unsupported UI controls or anti-bot challenges must fail gracefully, pausing the run and handing control back to the user.
5. OTP retrieval mechanisms and explicit approval pauses must be logged as first-class steps within the run timeline.

### 7. Inbox and OTP Integration
1. The system shall support user-authorized inbox connections specifically for retrieving application-related OTP codes.
2. OTP retrieval is strictly limited to identifying matching sender, subject, or code patterns from recently received emails.
3. Extracted OTP values must be aggressively masked in all logs and screenshots.
4. Low-confidence OTP retrievals must immediately pause the run and demand manual confirmation.
5. OAuth tokens must be stored using encrypted, environment-backed secret management paths.

### 8. Diagnostics and Administration
1. The system shall expose a comprehensive internal diagnostics panel detailing scrape-run statuses, prompt execution traces, and automation failures.
2. Audit records must be strictly preserved for all prompt usage, user approvals, OTP retrievals, and document exports.
3. Failed automation runs must present a retry action accompanied by the explicit failure reason and a link to the last successful checkpoint.

---

## 📊 Non-Functional Requirements

### Reliability
- The system must prioritize idempotent ingestion and establish reliable automation checkpoints.
- Failed application runs must support resumption from the last verified safe checkpoint.
- The architecture must tolerate partial failures (e.g., parsing errors, PDF fallback, scrape timeouts) without corrupting the broader user dataset.

### Performance
- The dashboard job feed must load latest events within **2 seconds** under normal localized datasets.
- Full tailored resume generation must complete within **10 seconds** for standard job descriptions.
- Automated OTP lookups must resolve (or gracefully fallback to a manual prompt) within **15 seconds**.

### Security
- All sensitive operations require strict authenticated user context.
- Integration secrets must be encrypted at rest.
- Secrets, tokens, OTPs, and sensitive prompt fragments must be actively masked in application logs.

### Observability
- The system must emit highly structured JSON logs covering scraping, scoring, tailoring, exporting, and executing.
- Prompt metadata and model routing decisions must be preserved without exposing raw secret inputs.
- Diagnostic tracing must be available at the per-job, per-role, and per-run level.

---

## 🚫 Explicitly Rejected Requirements

The following requests fundamentally violate the product vision and **shall not** be implemented under any circumstances:

1. Removing truth, approval, or safety guardrails from LLM prompt generation.
2. Guaranteeing a specific resume selection or interview success rate.
3. Fabricating qualifications, work history, or answers to artificially inflate application conversion rates.
4. Implementing mechanisms designed to actively bypass employer anti-bot controls, CAPTCHAs, or identity verification systems.