# ApplyForge Product Requirements

## Functional Requirements

### 1. Authentication and User Profiles
1. The system must support isolated user accounts secured via email/password authentication.
2. The system must provide users with full CRUD capabilities over their canonical profile.
3. Upon user registration, a default "starter" profile may optionally be populated based on environment configuration.
4. Profile settings must comprehensively support automation preferences, including job filters, auto-submit risk thresholds, and resume presentation defaults.

### 2. Candidate Brain (Resume Intelligence)
1. The system must parse uploaded resumes (PDF, DOCX, TXT) and intelligently extract structured sections: Basics, Summary, Skills, Experience, Projects, Education, Certifications, and Links.
2. The parsed `candidate_profiles` must remain fact-locked; the system is strictly prohibited from inventing skills or experience.
3. The system must securely persist "saved answers" derived from previous applications to rapidly accelerate future application runs.
4. A portable export (in both JSON and Text formats) of the user's combined automation profile must remain accessible at all times.

### 3. Resume Templates and Export
1. The system must feature a packaged catalog of ATS-friendly starter templates (Markdown and LaTeX).
2. The system must natively support template rendering against the canonical profile without altering underlying core profile data.
3. The system must utilize a structured generation pipeline (RenderCV-compatible) coupled with an internal PDF fallback to ensure export continuity.

### 4. Role Discovery and Job Feed
1. The system must allow users to define multiple `target_roles` encompassing aliases, keywords, locations, salary expectations, and visa requirements.
2. The system must facilitate the attachment of discovery sources (manual or packaged presets) to specific roles.
3. Scheduled or manual ingestion runs must automatically discover jobs from these sources, rigorously normalizing titles and employers.
4. The system must actively utilize deduplication keys (`dedupe_key`) to prevent the insertion of identical job postings.
5. Job lifecycles must be meticulously tracked via robust feed events (e.g., discovered, enriched, score_changed, expired).

### 5. Enrichment and Scoring
1. Discovered jobs must be asynchronously queued into a worker process for deeper metadata enrichment.
2. The system must attempt to resolve enriched jobs to known `companies` or `company_career_portals` where applicable.
3. A deterministic scoring engine must evaluate jobs by comparing the job's enriched requirements against the user's canonical profile and role strategy.
4. Scoring outputs must be fully transparent, distinctly exposing the overall score, specific strengths, missing skills, and detailed reasoning.
5. The system must natively support "fact-locked" tailoring, generating job-specific resume variants that emphasize relevant existing experience without hallucinating absent skills.

### 6. Application Execution (Automation)
1. The system must formally compile an "application packet" prior to initiating any run, consolidating tailored documents, resolved answers, and identified blocking risks.
2. Application runs must strictly adhere to a formal Finite State Machine (FSM) utilizing states: `queued`, `running`, `paused`, `failed`, `completed`, and `uncertain`.
3. The Playwright worker must durably capture and persist screenshot evidence and granular step logs across all execution attempts.
4. The system must automatically trigger a "pause" if it encounters risky questions (e.g., salary, visa status), unsupported controls, or CAPTCHA/anti-bot challenges.
5. Partial failures must preserve their state, allowing operators to manually inspect step histories and initiate retries.

### 7. Inbox and OTP Integration
1. The system must support optional OAuth connections to Gmail and Outlook to autonomously retrieve application-related One-Time Passwords (OTPs).
2. When an OTP is requested, the worker must scan recent messages, securely masking the retrieved code within logs and screenshots.
3. If OTP retrieval confidence is low, or if the timeout expires, the system must pause and gracefully degrade to request manual operator input.
4. Integration secrets and tokens must be strictly managed; missing configuration must be actively reported in the UI.

### 8. Diagnostics and Operator Tools
1. The system must expose comprehensive diagnostic panels for inspecting scrape run health, enrichment retry queues, and application run artifacts.
2. The system must maintain detailed audit logs concerning automation approvals, OTP retrievals, and executed profile exports.
3. Operators must possess the capability to manually transition paused or failed runs following necessary interventions.

## Non-Functional Requirements

### Reliability
1. Ingestion and automation routines must be highly idempotent.
2. The system must gracefully tolerate partial failures during scraping, parsing, or PDF generation without corrupting user data.

### Performance
1. Dashboard feeds should ideally load recent job events within 2 seconds.
2. Tailored resume generation should generally complete within 10 seconds under standard conditions.
3. OTP lookups must conclude or trigger a manual fallback within a reasonable timeframe (e.g., 15 seconds).

### Security
1. All sensitive actions must mandate authenticated user context.
2. The system must actively mask secrets, tokens, OTP codes, and sensitive prompt fragments within all application logs.
3. The system *shall not* allow the disabling of approval routing for fields identified as risky.

### Observability
1. The system must consistently emit structured, request-scoped logs for API and Worker operations.
2. The worker must preserve actionable trace evidence (e.g., screenshots, retry counts) for every application step.

## Core Product Invariants

1. **The Canonical Profile is Absolute:** It is the final authority over every generated document.
2. **No Hallucinations:** Tailoring may creatively optimize phrasing, but it is strictly forbidden from introducing unsupported facts or skills.
3. **Role Strategy Controls:** The role strategy dictates discovery logic and automation policies.
4. **Templates are Presentation Layers:** They dictate format, not the underlying source of truth.
5. **Durable Evidence:** Automation runs must always leave an inspectable audit trail.
6. **Scoped Inbox Access:** Inbox connections exist solely to facilitate the user's application flow; unrelated mail must remain untouched.

## Context Notes For Future Implementers
- **Job Sources:** Maintain deduplication and freshness semantics when integrating new sources.
- **Company Resolution:** Prioritize transparent matching heuristics and preserve user override capabilities.
- **Renderers:** If adding new renderers, adhere to the established normalized resume document schema.
- **Execution:** Keep `application_runs` and `application_steps` durable and human-readable when modifying worker behaviors.
- **OAuth:** Preserve encrypted token storage mechanisms if expanding OAuth provider support.

## Acceptance Criteria

1. **Profile Parsing:** When a user uploads a resume, a structured profile is generated; low-confidence fields are visibly flagged for review.
2. **Resume Export:** A user with multiple resume themes can effortlessly switch themes and export an ATS-friendly PDF.
3. **Role Discovery:** When an ingestion run triggers for a configured target role, new, deduplicated jobs dynamically populate the feed.
4. **Tailoring Integrity:** If a job requires skills the candidate lacks, the tailored resume emphasizes related experience but *does not* fabricate the missing skills.
5. **Guarded Automation:** When a "pause-before-submit" or risky question step is reached, the worker suspends execution and effectively surfaces screenshots and warnings for operator review.
6. **OTP Retrieval:** During an application run with an active inbox connection, arriving OTPs are automatically fetched, masked in logs, and utilized to proceed.
7. **Graceful Failures:** If an application hits a CAPTCHA or an unsupported field, the worker captures evidence, safely pauses the run, and prompts the user without crashing.
8. **Job Expiry:** Jobs no longer detected at their source are cleanly marked as expired, preserving historical automation data.

## Error Handling Scenarios

| Scenario | System Behavior | User-Facing Response |
|---|---|---|
| Resume parsing partially fails | Preserve raw text; log parse-failed event. | "We couldn't fully parse this resume. Review the extracted text or enter sections manually." |
| Primary PDF render fails | Fallback to default internal ATS renderer; preserve tailored text. | "This template failed to render. We switched to the default ATS template." |
| Source site rate-limits ingestion | Back off worker; mark run as partial; queue retry. | "This source is temporarily rate-limited. We'll retry automatically." |
| Duplicate job ingested | Merge necessary metadata; reject duplicate visible record. | "This job already exists in your feed. Source metadata was updated." |
| Required skills entirely missing | Lower automation score; explicitly highlight gaps. | "This job has missing required qualifications. Review before applying." |
| Unsupported application field | Pause run; capture screenshot and HTML evidence. | "This application contains an unsupported step. Review is required." |
| CAPTCHA / Anti-bot encountered | Pause run immediately; prompt user. | "Automation paused because the site requires human verification." |
| OTP email missing/timeout | Pause run; preserve browser session state. | "We couldn't retrieve the verification code. Enter it manually to continue." |
| Submit confirmation not detected | Mark run state as `uncertain`; request manual review. | "The application may not have been submitted. Please verify the final page." |

## Explicitly Rejected Requirements

The following requests fundamentally violate system safety and **shall not** be implemented:
1. Removing truth constraints or safety guardrails from prompt generation.
2. Architecting guarantees for a 100% resume selection or interview success rate.
3. Fabricating qualifications, experience, or answers to artificially inflate application conversion rates.
4. Engineering mechanisms designed to bypass employer anti-bot controls, CAPTCHAs, or verification systems.
