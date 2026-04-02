# ApplyForge Product Requirements

## Executive Summary

ApplyForge is a comprehensive job-hunt operating system designed for serious applicants. It consolidates the application lifecycle into a single, unified workflow:

1. **Profile Management:** Importing and structuring a master resume into a canonical database.
2. **Job Discovery:** Sourcing and ranking jobs in near real-time based on targeted role strategies.
3. **Document Generation:** Creating highly tailored, role-matched resumes and cover letters.
4. **Guarded Automation:** Preparing, reviewing, and executing browser-assisted job applications.
5. **Tracking and Analytics:** Monitoring application statuses, preserving run evidence, and managing follow-up actions.

This document formally defines the requirements for ApplyForge, specifically detailing the current product expansion encompassing ATS-friendly resume themes, real-time role scraping, company intelligence, advanced tailoring, step-based automation, and secure inbox integration for OTP retrieval.

## Product Invariants and Constraints

The following constraints are non-negotiable architectural and product mandates. They must be preserved across all future updates.

1. **No Guaranteed Outcomes:** ApplyForge optimizes for ATS readability and role relevance but **shall not** promise or guarantee specific interview or selection rates.
2. **Absolute Factual Integrity:** The system **shall not** invent, fabricate, or hallucinate resume facts, legal answers, salary histories, notice periods, work authorization statuses, or any other unknown candidate data.
3. **Strict Guardrails:** Safety-critical prompt guardrails governing truthfulness, risk detection, mandatory approval routing, and audit logging **shall not** be bypassed or removed.
4. **Ethical Inbox Access:** Inbox access for OTP retrieval is permitted **only** with explicit, informed user consent. It requires scoped credentials, comprehensive audit logs, and an accessible manual fallback path. The system must not scrape unrelated emails or expand user surveillance.
5. **Respect for Security Controls:** ApplyForge **shall not** attempt to bypass, solve, or circumvent CAPTCHAs, advanced anti-bot challenges, or legitimate employer security mechanisms.
6. **Data Isolation:** Company intelligence data must remain strictly user-scoped and inspectable unless a formal, global shared-directory architecture is explicitly implemented in the future.
7. **The Canonical Profile is Absolute:** The master candidate profile remains the ultimate, authoritative source of truth over any generated or tailored document.
8. **Role Strategy Dictates Policy:** User-defined role strategies drive discovery and automation policies; job-specific overrides are considered secondary.

## Target Audience

1. **Focused Job Seekers:** Individuals applying repeatedly for a specific, defined set of roles.
2. **Power Users:** Candidates managing multiple, distinct resume strategies for entirely different role families.
3. **Career Agencies/Coaches:** Professionals managing application pipelines for candidates in later stages of the job hunt.
4. **System Operators:** Internal administrators reviewing automation failures, prompt traces, and system health.

---

## Detailed Functional Requirements

### 1. Resume Templates and Structured Export

1. **Theme Availability:** The system must offer multiple light, ATS-friendly resume themes to users with a populated canonical profile.
2. **Built-in Options:** At minimum, the system must provide: *Classic ATS Light*, *Modern Minimal Light*, and *Compact Technical Light*.
3. **Live Preview:** Users must be able to preview the selected theme prior to initiating a PDF export.
4. **Theme Persistence:** The selected theme must be stored and associated with the specific resume version and tailored export.
5. **Machine Readability:** All exported PDFs must be machine-readable, containing selectable text and avoiding image-only content structures.
6. **ATS Compliance Enforcement:** The system must strictly enforce ATS-safe constraints. Multi-column or heavily decorative templates must be rejected or gracefully degraded when exported in ATS mode.
7. **Structured Intermediate State:** The system must preserve an intermediate, structured representation of the resume, allowing export engines (e.g., internal rendering, HTML-to-PDF, RenderCV) to be swapped dynamically.
8. **Export Continuity (Fallback):** If the primary rendering engine (e.g., RenderCV) fails at runtime, the system must seamlessly fall back to a safe, internal PDF renderer and log the original failure for diagnostic review.

### 2. Resume Upload and Canonical Profile

1. **Data Extraction:** The system must extract text from uploaded PDF, DOCX, or TXT files and parse it into structured canonical profile sections.
2. **Confidence Flagging:** Any profile section parsed with low confidence must be explicitly flagged for manual candidate review.
3. **Versioned Persistence:** The system must persist section-level, versioned updates whenever a user manually edits profile data.
4. **Single Source of Truth:** The system must support multiple target role strategies while strictly maintaining a single, fact-locked master profile.

### 3. Role Registry and Automation Preferences

1. **Role Definition:** Users must be able to define target roles containing: role name, aliases, keywords, preferred locations, remote preference, salary preference, visa requirements, seniority ranges, company inclusion/exclusion lists, and automation thresholds.
2. **Policy Enforcement:** Active target roles must strictly drive the job scraping pipeline, ranking algorithms, and automation eligibility.
3. **Scoring Base:** The system must maintain a stable table of role requirements and matching heuristics to enable deterministic job scoring against the intended role profile.

### 4. Real-time Job Scraper Engine

1. **Scheduled Ingestion:** The system must automatically scrape or ingest jobs on a defined schedule based on active target roles.
2. **Normalization:** All ingested jobs, regardless of source, must be normalized into a single, unified database schema prior to scoring or UI display.
3. **Robust Deduplication:** Jobs must be deduplicated across various sources utilizing a combination of the application URL, normalized company name, normalized title, and content fingerprints.
4. **Lifecycle Tracking:** The system must record precise metadata: first seen, last seen, ingestion source, associated scrape run, and current freshness status.
5. **Feed UX:** The system must expose a near real-time feed, allowing users to view source links, normalized details, and automation eligibility.
6. **Expiration Handling:** Jobs that disappear from the source must be marked as *inactive* or *expired*, preserving the historical record rather than performing a hard delete.
7. **Manual Import:** The system must support manual job import via direct URL or pasted text descriptions.
8. **Source Priority:** ATS-first sources (e.g., Greenhouse, Lever, Workday) and predictable direct career pages must be prioritized over broad, unstructured consumer job boards.

### 4A. Company Intelligence Directory

1. **Canonical Identity:** The system must support a user-scoped directory storing canonical company identity records (Name, Normalized Name, Website, Careers URL, LinkedIn URL, Location, Industry, Notes, Status).
2. **Portal Tracking:** The system must support tracking one or more career portals per company, including the provider type, base URL, board tokens, and structured-fetch capabilities.
3. **Contact Tracking:** The system must allow tracking of recruiter or HR contacts (Type, Source, Confidence, Verification Status) linked to the company record.
4. **Heuristic Resolution:** Newly ingested or manually created jobs must attempt to resolve to an existing company directory record using normalized names or hostnames.
5. **Override Protection:** Heuristic resolution must never silently overwrite an explicit, verified user selection.

### 5. Job Matching and Tailoring

1. **Dual-Axis Scoring:** Ingested jobs must be scored against **both** the canonical candidate profile and the specific target role strategy.
2. **Transparent Output:** Scoring outputs must detail: Overall Score, Role-Match Score, Skills Overlap, Missing Must-Haves, Nice-to-Have Overlap, Seniority Fit, Location Fit, Compensation Fit (if available), and a final Recommendation.
3. **Strict Tailoring Constraints:** When tailoring a resume, the system may only reorder, emphasize, summarize, or select from existing factual content.
4. **Gap Highlighting:** If a job requires a qualification the candidate lacks, the system must clearly highlight the gap. It must **never** fabricate coverage.
5. **Version Tracking:** Every tailored resume variant must persist diff metadata, the selected theme, and the linked job record.
6. **Automation Thresholds:** Jobs scoring below a user-defined threshold must default to having automation eligibility explicitly disabled.

### 6. Application Automation Engine

1. **Execution Modes:** The system must support Draft Mode (dry-run preparation), Assisted Mode (browser opened, pauses before submit), and Approved Auto Mode (fully automated execution based on policy).
2. **Durable Auditing:** Every automation run must persist: Run Status, Execution Mode, Timestamps, Per-Step Logs, Retry Counts, captured Screenshots, Structured Step Outputs, and Final Disposition.
3. **Risk Pauses:** Applications containing risky, legal, compensation-related, or ambiguous questions must force the FSM to pause and require explicit user approval.
4. **Graceful Failure:** Applications requiring unsupported controls or anti-bot validation must fail gracefully, preserving all gathered evidence and returning control to the user.
5. **OTP Representation:** OTP retrieval and explicit approval pauses must be represented as first-class, inspectable steps in the execution timeline.

### 7. Inbox Integration and OTP Access

1. **Consent-Driven Access:** The system must support user-authorized inbox connections specifically scoped for reading application-related OTPs and verification emails.
2. **Intelligent Retrieval:** When an OTP is requested by a run, the system must search recent messages using sender, subject, or pattern matching.
3. **Security Masking:** All retrieved OTP values must be rigorously masked in application logs and captured screenshots.
4. **Low-Confidence Pauses:** If OTP retrieval confidence is low or fails, the system must pause and request manual user input.
5. **Encrypted Storage:** Inbox credentials and OAuth tokens must be stored exclusively via encrypted, environment-backed, or secret-managed storage paths.
6. **Diagnostics:** OAuth connections (Gmail/Outlook) must expose clear setup readiness states and missing environment variables within the UI.

### 8. Diagnostics and Administration

1. **Internal Telemetry:** The system must expose scrape-run statuses, ingestion failures, prompt traces, automation errors, and screenshot artifacts within an internal diagnostics panel.
2. **Audit Retention:** Comprehensive audit records must be preserved for LLM prompt usage, automation approvals, OTP retrieval attempts, and resume exports.
3. **Actionable Retries:** Scrape or apply runs that fail must expose a distinct retry action, detailing the specific failure reason and identifying the last safe checkpoint.

---

## Non-Functional Requirements

### Reliability and Resilience
1. **Idempotency:** Ingestion and automation checkpoints must be highly idempotent.
2. **Checkpoint Recovery:** The system must support resuming failed application runs from the last safe, recorded checkpoint.
3. **Fault Tolerance:** Partial failures in scraping, parsing, PDF export, or browser automation must be contained and must not corrupt the canonical user data state.

### Performance Benchmarks
1. **Feed Rendering:** The dashboard feed must load the latest job events within 2.0 seconds under normal local-development datasets.
2. **Tailoring Speed:** Tailored resume generation must complete within 10.0 seconds for standard job descriptions.
3. **OTP Latency:** OTP lookup operations must resolve (either returning a result or triggering the manual fallback prompt) within 15.0 seconds.

### Security and Privacy
1. **Strict Authentication:** All sensitive actions (auth, inbox, automation) require heavily validated, authenticated user contexts.
2. **Data Encryption:** Sensitive integration secrets must be encrypted at rest.
3. **Log Sanitization:** Secrets, tokens, OTP codes, and sensitive prompt fragments must be strictly masked or omitted from application logs.

---

## Acceptance Criteria

1. **Resume Upload:** Given a user uploads a resume, when parsing finishes, then the user can review a structured profile and see any low-confidence fields explicitly flagged for edit.
2. **Theme Switching:** Given a user has multiple resume themes available, when they open a tailored resume, then they can switch the theme and export an ATS-friendly PDF preview successfully.
3. **Feed Delivery:** Given a user creates a target role, when scraping runs, then new normalized jobs appear in a feed tagged to that specific role and sorted by freshness.
4. **Deduplication:** Given the exact same job is discovered from two separate sources, when ingestion completes, then only one active job record remains, but both source references are durably retained.
5. **No Hallucinations:** Given a job has required skills the user does not possess, when tailoring runs, then the tailored resume highlights relevant experience but completely refrains from fabricating the missing skills.
6. **Assisted Pausing:** Given Assisted Mode is initiated, when the application reaches the final submit step, then the run explicitly pauses and presents screenshots, filled values, and warnings for user review.
7. **Risk Routing:** Given an application asks a risky or ambiguous question, when answer generation runs, then the system marks the step as `Approval Required` instead of automatically answering.
8. **OTP Retrieval:** Given inbox access is enabled, when an OTP email arrives during a run, then the system successfully retrieves the code, masks it in logs, and continues the run only if the user policy permits.
9. **OTP Fallback:** Given OTP retrieval fails or confidence is low, when the timeout expires, then the system pauses gracefully and requests manual input without losing the browser or run state.
10. **Expiration:** Given a previously scraped job is no longer available at the source, when the feed refreshes, then the job is marked `inactive/expired`, ensuring previous automation records remain fully visible.

---

## Error Handling Matrix

| Scenario | System Behavior | User-Facing Response |
|---|---|---|
| Resume parsing fails | Preserve upload, emit `parse-failed` event, enable manual creation. | *"We couldn't fully parse this resume. Review the extracted text or enter sections manually."* |
| Resume theme render fails | Retain tailored content, fall back to default ATS theme, log error. | *"This template failed to render. We switched to the default ATS template."* |
| Source site rate limit hit | Back off scrape worker, mark run partial, queue retry. | *"This source is temporarily rate-limited. We'll retry automatically."* |
| Duplicate job ingested | Merge new source metadata into existing record; drop duplicate. | *"This job already exists in your feed. Source metadata was updated."* |
| Missing Must-Have skill | Highlight gap explicitly, lower automation eligibility score. | *"This job has missing required qualifications. Review before applying."* |
| Unsupported application field | Pause run, capture DOM/screenshot evidence. | *"This application contains an unsupported step. Review is required."* |
| CAPTCHA / Anti-Bot trigger | Halt automation immediately, require manual user intervention. | *"Automation paused because the site requires human verification."* |
| OTP email not found | Pause run, preserve browser state if possible. | *"We couldn't retrieve the verification code. Enter it manually to continue."* |
| Inbox token invalid/expired | Disconnect integration locally, mark run as blocked. | *"Your inbox connection needs to be re-authorized."* |
| Submit confirmation failure | Mark FSM run as `uncertain`, require manual user verification. | *"The application may not have been submitted. Please verify the final page."* |

---

## Explicitly Rejected Requirements

The following requests have been evaluated and are explicitly rejected. They **shall not** be implemented under any circumstances:

1. Removing truth, approval, or safety guardrails from generative AI prompts.
2. Guaranteeing, promising, or marketing a 100% resume selection or interview success rate.
3. Fabricating, hallucinating, or exaggerating qualifications or answers to artificially inflate application conversion rates.
4. Implementing logic specifically designed to bypass or defeat employer anti-bot controls, CAPTCHAs, or verification systems.
