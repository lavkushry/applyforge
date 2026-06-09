# ApplyForge Product Requirements

This document outlines the functional and non-functional requirements governing the ApplyForge system. It serves as the definitive reference for expected behavior, architectural invariants, and the criteria for accepting new features.

## Functional Requirements

### 1. Account & Identity Management
1. The system must support user registration and authentication via an email/password combination.
2. The system must issue secure, HTTP-only, cookie-backed JWTs for session management.
3. All profile data, scraped jobs, and application records must be strictly isolated to the authenticated user's scope.
4. The system must provide endpoints to refresh and invalidate active user sessions.

### 2. Candidate Profile & Resume Parsing
1. The system must allow users to upload source resumes in PDF, DOCX, and plain text formats.
2. The system must parse uploaded resumes and extract text into a structured, canonical profile (encompassing skills, work history, projects, and education).
3. The system must provide a user interface for manually editing, correcting, or augmenting the extracted profile data.
4. The system must preserve user-defined preferences regarding job filtering and automation policies.

### 3. Role Strategy & Job Discovery
1. The system must allow users to define "Target Roles" that dictate job discovery criteria (e.g., titles, keywords, location preferences, salary thresholds).
2. The system must support subscribing these Target Roles to specific job sources (e.g., direct career pages, ATS boards).
3. The system must execute scheduled discovery runs to ingest new job postings based on active Target Role subscriptions.
4. The system must implement robust deduplication, ensuring that identical jobs found across multiple sources resolve to a single, unique record in the user's feed.
5. The system must maintain an auditable timeline of feed events for each job (e.g., `discovered`, `enriched`, `score_changed`, `expired`).

### 4. Data Enrichment & Intelligence
1. The system must differentiate between raw job discovery and deep data enrichment.
2. The system must queue newly discovered jobs for asynchronous worker-based enrichment to extract structured requirements and metadata.
3. The system must attempt to resolve job postings to known entities within the Company Intelligence Directory, leveraging heuristics like URLs and normalized names.
4. If an external job posting becomes inactive, the system must update its status to `expired` while preserving all historical automation records.

### 5. Algorithmic Scoring & Resume Tailoring
1. The system must calculate a match score for enriched jobs based on the user's canonical profile and the active Target Role strategy.
2. The scoring output must be transparent, explicitly detailing identified strengths, missing requirements, and the reasoning behind the final recommendation.
3. The system must generate tailored resume variants specifically optimized for a given job.
4. **Invariant:** The tailoring process may emphasize relevant existing skills and rephrase descriptions for clarity, but it is strictly prohibited from fabricating experience, skills, or credentials not present in the canonical profile.
5. The system must support generating ATS-friendly PDF exports utilizing an array of built-in templates, with a reliable fallback mechanism if the primary renderer fails.
6. The system must generate tailored cover letters corresponding to the specific job requirements and candidate profile.

### 6. Application Automation & Orchestration
1. The system must compile a comprehensive "application packet" (including the tailored resume, cover letter, and pre-calculated answers) prior to initiating an execution run.
2. The system must manage application runs through a strict Finite State Machine (FSM) utilizing defined states (`queued`, `running`, `paused`, `failed`, `completed`, `uncertain`).
3. During assisted or automated runs, the system must only auto-submit applications that fall within the user's defined risk and automation thresholds.
4. The system must durably persist evidence for every step of an automation run, including timestamps, raw logs, retry counts, and captured browser screenshots.
5. The system must force a manual pause requiring explicit user approval if an application demands answers to high-risk questions (e.g., salary expectations, visa status, legal disclosures).
6. The system must gracefully pause and return control to the user if it encounters unsupported UI controls, CAPTCHAs, or other anti-bot verification mechanisms.

### 7. Inbox Integration & OTP Handling
1. The system must allow users to authorize access to their Gmail or Outlook inboxes strictly for the purpose of retrieving application-related One-Time Passwords (OTPs).
2. During an automation run, the system must search the connected inbox for relevant OTP emails using targeted sender and subject heuristics.
3. All retrieved OTPs and related sensitive tokens must be heavily masked in system logs and screenshot artifacts.
4. If the system cannot confidently retrieve an OTP, it must pause the run and await manual input from the user without losing the browser's current state.
5. OAuth tokens must be stored securely using encryption at rest.

### 8. Diagnostics & Operator Tools
1. The system must provide an internal diagnostic dashboard exposing the status of scrape runs, enrichment failures, prompt traces, and automation errors.
2. The system must maintain audit logs tracking LLM prompt usage, user approvals during automation, and document export events.
3. The system must allow operators to view execution screenshots and trigger retries for failed tasks directly from the UI.

## Non-Functional Requirements

### Reliability & Resilience
1. Ingestion routines and automation steps must be idempotent where possible to safely handle retries.
2. The system must support resuming paused or failed application runs from the last successfully recorded checkpoint.
3. The architecture must gracefully tolerate partial failures (e.g., a PDF renderer failing should not corrupt the underlying profile data).

### Performance Metrics
1. The frontend job feed must render the latest events within 2 seconds using typical local development datasets.
2. Generating a fully tailored resume must complete within 10 seconds under standard conditions.
3. Automated OTP retrieval must either succeed or trigger a manual fallback prompt within 15 seconds.

### Security Posture
1. All API endpoints handling user data, inbox connections, and automation triggers must enforce strict authentication.
2. Third-party API keys and integration secrets must be encrypted at rest and managed via environment variables.
3. System logs must proactively sanitize sensitive data, including OTP codes and PII.

## Fundamental Product Invariants
*These rules represent the core philosophy of ApplyForge and must not be violated by future updates.*

1. **The canonical profile is authoritative:** It supersedes all generated content.
2. **No Hallucinations:** Document tailoring and question answering may optimize phrasing but must never invent facts.
3. **Presentation vs. Data:** Resume themes are purely a presentation layer; they do not serve as a source of truth for candidate data.
4. **Strategy Dictates Action:** The user's broader role strategy governs discovery and automation, overriding individual job quirks.
5. **Auditable Execution:** Every automation run must leave a clear, inspectable trail of evidence explaining its outcome.
6. **Scoped Inbox Access:** Inbox integrations exist solely to facilitate the user's application process; the system must not surveil or scrape unrelated emails.

## Excluded Functionality
*The following features are explicitly rejected and will not be implemented:*

1. Removing the fact-checking guardrails from LLM prompt generation.
2. Guaranteeing specific interview conversion rates.
3. Falsifying qualifications or generating fake answers to force application submissions.
4. Implementing adversarial techniques to bypass employer CAPTCHAs or anti-bot systems.
