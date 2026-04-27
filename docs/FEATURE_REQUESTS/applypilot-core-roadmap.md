# ApplyPilot-Core Roadmap Status

## Document Purpose

This document serves as a status report detailing the implementation progress of the "ApplyPilot-style" roadmap within ApplyForge. It is no longer a greenfield feature request, but rather an account of what has been shipped and what work remains.

The fundamental operational shape remains consistent:
1.  Discover
2.  Enrich
3.  Score
4.  Tailor
5.  Prepare
6.  Execute

## Implementation Status

### 1. Discovery
**Status:** Substantially Implemented

*   **Shipped:**
    *   Role-driven source subscriptions.
    *   Packaged discovery presets and search templates.
    *   Discovery-first data ingestion runs.
    *   System feed events tracking job lifecycles (discovered, enriched, score-changed, expired).
    *   MVP-level support for major platforms (Greenhouse, Lever, Workday) and direct-source extraction.
*   **Remaining Work:**
    *   Expanding the breadth of source coverage.
    *   Implementing robust source-health diagnostics.
    *   Enhancing direct-site extraction fidelity.

### 2. Enrichment
**Status:** Substantially Implemented

*   **Shipped:**
    *   An explicit architectural split separating discovery from enrichment.
    *   Worker-queued enrichment tasks executed per job.
    *   Tracking of enrichment status, associated metadata, and revision history.
    *   Linkage of source snapshot artifacts to job records.
*   **Remaining Work:**
    *   Improving the quality and depth of structured data extraction.
    *   Exposing detailed retry and backoff metrics to operators.
    *   Developing advanced, cascading extraction logic.

### 3. Scoring
**Status:** Substantially Implemented

*   **Shipped:**
    *   Context-aware scoring based on target roles.
    *   Actionable recommendation outputs.
    *   Detailed breakdowns of strengths, missing skills, and transparent reasoning.
    *   Score snapshots definitively tied to specific enrichment revisions.
*   **Remaining Work:**
    *   Integrating stronger semantic matching and ontological analysis.
    *   Improving calibration for compensation and visa requirements.
    *   Developing more nuanced application readiness scoring.

### 4. Tailoring
**Status:** Substantially Implemented

*   **Shipped:**
    *   Strictly fact-locked document tailoring capabilities.
    *   Targeted emphasis on relevant skills, experiences, and projects.
    *   Diff metadata surfacing matched versus uncovered job requirements.
    *   Theme-aware generation of resume versions.
    *   Automated cover letter generation.
*   **Remaining Work:**
    *   Implementing sophisticated ranking algorithms for experience bullets.
    *   Supporting reusable, multi-strategy resume families.
    *   Increasing the visual fidelity between the web preview and final PDF export.

### 5. Preparation
**Status:** Substantially Implemented

*   **Shipped:**
    *   Generation of formal, structured application packets.
    *   Preflight readiness checks executed prior to automation.
    *   Resolution of application answers complete with data provenance.
    *   Packet summaries integrated into application UX surfaces.
*   **Remaining Work:**
    *   Developing deeper, predictive analysis to identify unsupported fields *before* runtime execution.
    *   Providing richer packet diagnostics within administrative views.

### 6. Execution
**Status:** Substantially Implemented

*   **Shipped:**
    *   API-driven creation of queued execution runs.
    *   Worker-backed application execution via Playwright.
    *   Durable, step-by-step logging of execution events.
    *   Persistent screenshot capture stored as `uploaded_files`.
    *   Automated detection of anti-bot mechanisms triggering a safe "pause" state.
    *   Assisted "pause-before-submit" checkpoints.
    *   OTP retrieval treated as a first-class execution step.
    *   Formalized state transitions via the Run FSM.
    *   Operator intervention actions (resume/fail) for paused and uncertain runs.
*   **Remaining Work:**
    *   Broadening coverage of Playwright field adapters.
    *   Engineering robust navigation for complex, multi-page ATS flows.
    *   Refining heuristics for confirming successful application submission.
    *   Developing more sophisticated restart and recovery semantics.

## Architectural Baseline Shifts

The original roadmap treated the following components as future aspirations; they are now implemented and constitute the baseline architecture:
*   Celery worker dispatch as the primary execution pathway.
*   A persistent, formal application packet data model.
*   Durable capture of step evidence (logs and screenshots).
*   Rigorous run status transitions managed by a Finite State Machine.

## Strategic Priorities

Moving forward, development efforts should focus on:
1.  **Adapter Coverage**: Expanding field adapter capabilities to handle diverse ATS controls and complex multi-page forms.
2.  **Extraction Quality**: Enhancing direct-site enrichment depth and implementing comprehensive source-health diagnostics.
3.  **Intelligence Depth**: Strengthening the semantic quality of scoring and tailoring, moving beyond simple keyword matching.
4.  **Operator Visibility**: Improving administrative dashboards regarding task retries, packet composition, and system failures.
5.  **OAuth Resilience**: Hardening live provider verification and implementing robust OAuth recovery workflows.

## Non-Negotiable Guardrails

All future development must adhere to these established guardrails:
1.  The canonical candidate profile remains the ultimate, authoritative source of truth.
2.  Automated tailoring mechanisms must never invent or fabricate facts.
3.  Risky, sensitive, or unknown application answers must remain strictly approval-gated.
4.  Sensitive outputs (tokens, OTPs) must be securely masked.
5.  Encounters with CAPTCHAs or anti-bot flows must result in an operational pause, never an attempt to bypass.
