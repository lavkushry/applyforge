# ApplyForge Product Specifications

## Platform Vision

ApplyForge is an end-to-end Job Hunt Operating System. It centralizes and automates the fragmented processes of modern job seeking into a single, unified pipeline:

1. **Intelligent Ingestion**: Parsing and structuring a master candidate profile from raw resume files.
2. **Targeted Aggregation**: Scraping and scoring job postings in near real-time based on defined role strategies.
3. **Dynamic Generation**: Crafting role-specific, factually accurate tailored resumes and cover letters.
4. **Guarded Automation**: Executing browser-based job applications with human-in-the-loop safeguards.
5. **Operational Telemetry**: Tracking the status, visual evidence, and inbox communications of every application attempt.

## Fundamental Product Rules (Invariants)

These constraints are non-negotiable and dictate the boundaries of all future feature development:

1. **No Hallucinations Guarantee**: The system will aggressively optimize layout and phrasing, but it is strictly prohibited from inventing skills, fabricating metrics, guessing legal status, or lying about compensation.
2. **Canonical Profile Authority**: The master candidate profile is the immutable source of truth. Rendered templates and tailored outputs are merely views derived from this core data.
3. **Safety Through Pausing**: The automation engine cannot autonomously bypass CAPTCHAs, invent answers to missing mandatory fields, or submit sensitive data (e.g., SSNs, visa status) without explicit user approval.
4. **Transparent Telemetry**: If an automated application fails, the user must be able to see exactly why via preserved screenshot artifacts and step-by-step logs.
5. **Scoped Access Control**: Integrating external inboxes (Gmail/Outlook) is solely for the purpose of retrieving necessary OTPs (One-Time Passwords). It requires explicit consent and must fail gracefully to manual input if retrieval fails.

## Core Feature Requirements

### 1. Resume Parsing & Profile Management
- The system must extract text from uploaded PDF, DOCX, and TXT files and organize it into discrete profile sections (Experience, Education, Skills, etc.).
- Low-confidence data extractions must be visually flagged to prompt user review.
- The user interface must allow granular, section-by-section editing of the profile, maintaining a versioned history of changes.
- The profile must also capture fixed automation preferences (e.g., minimum salary requirements, remote work policies).

### 2. Job Discovery & Role Registry
- Users define "Target Roles" encompassing keywords, desired locations, excluded companies, and automation thresholds.
- Scheduled background tasks will ingest job postings from attached sources (boards, career pages) based on these Target Roles.
- Ingested jobs must undergo a normalization process to deduplicate identical postings across different job boards using URL and company metadata.
- The UI must present a real-time feed of discovered roles, allowing users to track job freshness (new, enriched, expired).

### 3. Company Directory Integration
- The system must support a standalone directory of canonical "Company" records, encompassing names, domains, career portals, and ATS provider types.
- Scraped jobs must attempt heuristic resolution against the Company Directory to link isolated job listings to holistic company profiles.
- Company profiles should additionally store recruiter contacts and specific corporate notes.

### 4. Tailoring & Fit Scoring
- Every discovered job must be scored against both the Canonical Profile and the associated Target Role strategy.
- Scoring outputs must provide a human-readable breakdown distinguishing between matched skills, missing mandatory requirements, and overall alignment.
- Tailoring operations will generate job-specific resume variants by reordering and emphasizing relevant bullet points, stopping short of altering factual history.
- Jobs scoring below the user’s defined threshold automatically lose eligibility for autonomous application submission.

### 5. Document Templating & Export
- The platform must offer a selection of pre-built, ATS-friendly light themes (e.g., Classic, Modern, Compact).
- Users can preview their tailored profile data injected into these themes via the web interface.
- PDF generation must produce fully text-extractable documents (no image-only outputs) to ensure downstream ATS compatibility.
- The core export pipeline should utilize a RenderCV-compatible adapter, backed by an internal fallback generator to ensure PDF generation never experiences total downtime.

### 6. Application Execution (The Worker)
- The application workflow supports three paradigms:
  - **Draft**: Preparing the packet and warning of missing data without launching a browser.
  - **Assisted**: Opening the browser, filling forms, and deliberately halting before final submission.
  - **Auto**: End-to-end execution, restricted only to jobs meeting the strict risk and score thresholds.
- The worker must gracefully handle multi-page navigation, standard text inputs, dropdowns, radio buttons, and document uploads.
- A rigid Finite State Machine (FSM) will dictate the lifecycle of a run (e.g., transitioning from `queued` to `running`, `paused`, or `failed`).
- Playwright-driven step executions must securely capture and upload screenshots for subsequent audit review.

### 7. Inbox Interception (OTP Automation)
- Users may authorize OAuth connections to Gmail or Outlook to facilitate seamless application logins.
- When an application flow requires an OTP, the system queries the inbox for recent matches against the sender domain.
- Successful OTP retrievals must be masked in the application logs to protect account security.
- Failure to locate an OTP within the timeout window triggers an automatic FSM pause, allowing the user to provide the code manually.

## Explicitly Out of Scope
The following features are rejected and must not be implemented:
- Automated CAPTCHA solving modules or third-party circumvention tools.
- Generative AI prompt configurations instructed to "fake it till you make it" to increase application volume.
- Guaranteed placement claims or interview success rate promises.