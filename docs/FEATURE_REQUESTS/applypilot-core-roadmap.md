# ApplyPilot-Core Roadmap: Implementation Status

## Context

This document tracks the progress of the ApplyForge platform against the original ApplyPilot-inspired roadmap. It has evolved from a feature request document into an implementation status report.

The core pipeline envisioned—Discover -> Enrich -> Score -> Tailor -> Prepare -> Execute—remains the guiding structure.

## Current Implementation Status

### 1. Job Discovery
**Implemented:**
- Job source subscriptions driven by target roles.
- Support for packaged discovery configurations and reusable search templates.
- Initial ingestion runs prioritizing discovery.
- A robust event feed tracking jobs through `discovered`, `enriched`, `score-changed`, and `expired` states.
- Initial support for common platforms (Greenhouse, Lever, Workday) and direct-source parsing.

**Pending Enhancements:**
- Expanding the breadth of supported job sources.
- Improving diagnostics to monitor the health and uptime of job sources.
- Refining direct-site text extraction capabilities.

### 2. Data Enrichment
**Implemented:**
- Clear architectural separation between initial discovery and subsequent enrichment.
- A worker-based queue system handling asynchronous job enrichment.
- Tracking of enrichment statuses, metadata, and versioning (revisions).
- Saving snapshot artifacts from the original job source.

**Pending Enhancements:**
- Improving the accuracy and structure of the extracted data.
- Exposing detailed retry logic and backoff schedules to the system operator.
- Implementing more complex, cascading extraction rules.

### 3. Match Scoring
**Implemented:**
- Dynamic scoring based on the specific target role.
- Generation of actionable recommendations.
- Identification of candidate strengths, missing skills, and detailed reasoning for the score.
- Archiving score snapshots tied directly to specific enrichment revisions.

**Pending Enhancements:**
- Integrating stronger semantic matching and deeper ontological understanding.
- Refining the calibration for compensation and visa requirement matches.
- Developing more sophisticated scoring for application readiness.

### 4. Resume Tailoring
**Implemented:**
- Strict, fact-locked tailoring ensuring no fabrication of experience.
- Algorithmic emphasis on relevant skills, historical experience, and specific projects.
- Detailed diff generation highlighting both matched requirements and uncovered gaps.
- Exporting tailored resumes using multiple theme variants.
- Automated cover letter generation.

**Pending Enhancements:**
- Improving the ranking logic for individual experience bullet points.
- Supporting multi-strategy resume families that can be reused.
- Ensuring the web-based preview more accurately reflects the final PDF export.

### 5. Application Preparation
**Implemented:**
- Assembly of formal "application packets."
- Execution of preflight readiness checks before allowing a submission attempt.
- Resolution of application questions with clear provenance back to the canonical profile.
- Summarization of the packet within the application tracking UI.

**Pending Enhancements:**
- Enhancing the system's ability to predict unsupported field types before execution begins.
- Providing deeper, more actionable diagnostic tools for application packets within the admin interface.

### 6. Automated Execution
**Implemented:**
- API-driven creation of queued application runs.
- Utilizing the asynchronous worker for both enrichment and active application execution.
- Durable, step-by-step logging of the execution process.
- Storing browser screenshots as uploaded file artifacts for later review.
- Identifying anti-bot mechanisms and automatically pausing the run.
- Supporting an "assisted mode" that pauses for human review before final submission.
- Treating OTP retrieval as a native, trackable step in the execution pipeline.
- Enforcing strict Finite State Machine (FSM) transitions for run statuses.
- Providing the operator with actions to handle paused, failed, or uncertain runs.

**Pending Enhancements:**
- Expanding the library of field adapters to cover a wider variety of ATS controls.
- Improving handling for complex, multi-page application flows.
- Developing more reliable heuristics to confirm successful application submissions.
- Enhancing the logic for restarting runs from intermediate checkpoints.

## Significant Architectural Shifts
Since the initial roadmap, several key components have moved from theoretical concepts to baseline infrastructure:
- The async worker dispatch system is now the primary execution path.
- The concept of a persistent "application packet" is fully realized in the data model.
- Step-by-step execution evidence is now durably stored.
- State transitions are now governed by a formal FSM.

## Ongoing Priorities
Future development efforts should focus on:
1. Expanding field adapter capabilities to handle more diverse and complex ATS structures.
2. Deepening direct-site enrichment and improving source-health monitoring.
3. Enhancing the qualitative accuracy of the scoring and tailoring algorithms.
4. Upgrading the admin interfaces to better manage retries, inspect packets, and diagnose failures.
5. Implementing live validation for OAuth providers and robust recovery flows for broken connections.

## Immutable Safety Rules
These principles remain non-negotiable regardless of future roadmap changes:
1. The user's canonical profile is the definitive source of truth.
2. Tailoring processes are strictly forbidden from inventing facts.
3. Questions carrying high risk or lacking confident answers must trigger a manual approval gate.
4. Sensitive data (like OTPs) must be heavily masked in logs and interfaces.
5. Encounters with CAPTCHAs or anti-bot measures must pause the automation rather than attempt bypass.
