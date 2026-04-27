# ApplyForge Product Requirements

This document defines the core invariants, acceptance criteria, and explicit boundaries governing the ApplyForge platform. These requirements must be upheld across all future architectural and feature updates.

## Core System Invariants

1.  **Authoritative Profile**: The canonical candidate profile acts as the single, trusted source of truth for all user data and resume facts.
2.  **Fact-Locked Generation**: Automated processes (tailoring, cover letter generation, question answering) may optimize phrasing but **shall never** fabricate unsupported facts or qualifications.
3.  **Presentation Separation**: Resume themes and templates are strictly presentation layers; they must not become parallel sources of user data.
4.  **Role-Driven Strategy**: The configuration of "Target Roles" dictates the policies governing job discovery and application automation. Job-specific overrides are considered secondary.
5.  **Durable Auditability**: Application automation must generate a durable, human-readable audit trail (including step logs and screenshots) providing sufficient evidence to understand system behavior, even upon failure.
6.  **Restricted Inbox Scope**: Inbox access (OAuth) exists solely to assist candidates in completing their specific application workflows (e.g., OTP retrieval). It shall not be used for general surveillance or scraping unrelated communications.

## Security and Privacy Requirements

### Access Control
1.  All authentication, inbox access, and automation-sensitive actions shall require a valid, authenticated user context.
2.  The system shall not bypass approval routing for questions deemed high-risk (e.g., salary expectations, visa requirements).

### Data Protection
1.  The system shall encrypt or otherwise secure sensitive integration secrets (e.g., OAuth tokens) at rest.
2.  The system shall actively mask secrets, tokens, OTP codes, and sensitive prompt fragments within all application and operational logs.

### Observability
1.  The system shall emit structured logs detailing scrape runs, score generation, document tailoring, PDF exports, and application automation workflows.
2.  The system shall preserve LLM prompt metadata and model routing information without exposing raw secrets.
3.  The system shall support robust diagnostic views aggregated per job, per target role, and per application run.

## Acceptance Criteria

### Resume and Profile Management
1.  **Given** a user uploads a resume file, **when** the parsing process completes, **then** the user can review a structured profile and clearly identify any fields flagged as low-confidence requiring manual review.
2.  **Given** a user has access to multiple resume themes, **when** they review a tailored resume, **then** they can seamlessly switch themes and export a valid, ATS-friendly PDF.

### Job Discovery and Processing
3.  **Given** a user configures a target role, **when** the background scraping routine executes, **then** newly discovered, normalized jobs appear in a feed associated with that role, ordered by freshness.
4.  **Given** identical job listings are discovered across multiple sources, **when** ingestion finishes, **then** only a single, deduplicated job record remains active, retaining metadata from all original sources.
5.  **Given** a job posting becomes unavailable, **when** the feed refreshes, **then** the job is marked as inactive or expired, while preserving previous automation records and visibility.

### Automation and Tailoring
6.  **Given** a target job requires skills absent from the user's profile, **when** document tailoring executes, **then** the generated resume highlights the closest relevant experience but strictly refuses to fabricate the missing skills.
7.  **Given** the "assisted application" mode is initiated, **when** the automation reaches the final submission stage, **then** the run pauses, presenting screenshots, populated values, and system warnings for manual review.
8.  **Given** an application form presents a risky or ambiguous question, **when** answer generation executes, **then** the system bypasses auto-answering and marks the step as requiring explicit manual approval.
9.  **Given** an application form contains an unsupported field type, **when** automation encounters it, **then** the system pauses, captures contextual evidence, and requests manual intervention.
10. **Given** a CAPTCHA or anti-bot challenge is presented, **when** automation detects it, **then** the system pauses the run and requires manual completion by the user.

### Inbox and OTP Workflows
11. **Given** inbox access is enabled, **when** an OTP verification email arrives during an application run, **then** the system retrieves the code, masks it in logs, and proceeds according to policy.
12. **Given** OTP retrieval fails or system confidence is low, **when** the timeout threshold is reached, **then** the system pauses the run, requests manual input, and preserves the current browser state.
13. **Given** an inbox OAuth token becomes invalid, **when** an operation requires it, **then** the system disconnects the integration, marks the current run as blocked, and prompts the user for re-authorization.
14. **Given** submission confirmation cannot be programmatically verified, **when** the run concludes, **then** the system marks the run state as "uncertain" and requires manual user verification of the final page.

## Explicitly Rejected Requirements

To maintain system integrity and user trust, the following requests are explicitly rejected and **shall not** be implemented:

1.  Removing truth requirements, approval gates, or safety guardrails from LLM prompt generation.
2.  Guaranteeing or falsely advertising a 100% resume selection or interview conversion rate.
3.  Fabricating qualifications, job experiences, or answers to artificially inflate application scoring or conversion metrics.
4.  Developing or deploying mechanisms designed to bypass, defeat, or circumvent employer anti-bot controls, CAPTCHAs, or human verification systems.
