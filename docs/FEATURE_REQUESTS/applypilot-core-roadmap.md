# ApplyPilot-Core Roadmap Status

## Purpose

This document serves as an active status record detailing the implementation of the ApplyPilot-style architecture within ApplyForge. It transitions this roadmap from a greenfield feature request into a definitive ledger of completed foundations and remaining technical debt.

The architectural target remains focused on a six-stage pipeline:

1. **Discover**
2. **Enrich**
3. **Score**
4. **Tailor**
5. **Prepare**
6. **Execute**

This document tracks the maturity of each stage.

---

## Current Implementation Status

### 1. Discovery
**Status:** Core capabilities established.
- **Completed:**
  - Role-driven source subscriptions.
  - Packaged discovery presets and structured search templates.
  - Discovery-first ingestion pipelines.
  - Comprehensive feed event tracking (discovered, enriched, score-changed, expired).
  - MVP-level support for major platforms (Greenhouse, Lever, Workday-style, and direct-source configurations).
- **Remaining Needs:**
  - Broader source coverage and platform breadth.
  - Dedicated source-health diagnostic reporting.
  - More resilient direct-site extraction logic.

### 2. Enrichment
**Status:** Pipeline established; execution needs hardening.
- **Completed:**
  - Explicit architectural split between discovery and enrichment phases.
  - Worker-queued, asynchronous enrichment tasks per job.
  - Tracking for enrichment status, metadata, and data revision history.
  - Durable linkage to source snapshot artifacts.
- **Remaining Needs:**
  - Improvements to structured data extraction quality.
  - Greater operator visibility into queue depth, retries, and backoff metrics.
  - Implementation of advanced fallback and cascading extraction strategies.

### 3. Scoring
**Status:** Fully functional MVP.
- **Completed:**
  - Context-aware scoring utilizing defined target roles.
  - Actionable recommendation outputs.
  - Transparent breakdowns highlighting strengths, missing skills, and detailed reasoning.
  - Score snapshotting directly tied to specific enrichment revisions.
- **Remaining Needs:**
  - Implementation of advanced semantic matching or a formal skills ontology.
  - Tighter calibration for compensation and visa requirement scoring.
  - Advanced candidate readiness heuristics.

### 4. Tailoring
**Status:** Core guardrails active and exporting correctly.
- **Completed:**
  - Strict, fact-locked resume tailoring (no hallucination).
  - Intelligent emphasis of highly relevant skills, experience, and projects.
  - Diff metadata generation (tracking matched vs. uncovered requirements).
  - Theme-aware resume versioning and export capabilities.
  - Context-aware cover letter generation.
- **Remaining Needs:**
  - Smarter, context-driven ranking for experience bullet points.
  - Support for reusable, multi-strategy resume families.
  - Improved fidelity between the web UI preview and the final PDF export.

### 5. Preparation
**Status:** Data structures implemented.
- **Completed:**
  - Generation of formal application packets prior to execution.
  - Pre-flight readiness checks to flag blocking issues.
  - Resolution of answers mapped to distinct data provenance.
  - Comprehensive packet summaries surfaced in the application UI.
- **Remaining Needs:**
  - Stronger predictive logic to flag unsupported form fields *before* runtime execution.
  - Richer packet diagnostic tools available within the administrative UI.

### 6. Execution
**Status:** Worker operational; field coverage requires expansion.
- **Completed:**
  - API-driven queued run creation.
  - Worker-backed execution for both job enrichment and application submissions.
  - Durable logging of individual execution steps.
  - Persistent screenshot capture, stored as uploaded file artifacts.
  - Anti-bot detection mechanisms triggering graceful pauses.
  - Assisted "pause-before-submit" workflows.
  - First-class run step integration for OTP retrieval.
  - Governance via a formal run Finite State Machine (FSM).
  - Operator controls allowing resumes to be actioned from paused, failed, or uncertain states.
- **Remaining Needs:**
  - Significantly broader field adapter coverage.
  - Enhanced robustness for handling complex, multi-page ATS flows.
  - Stronger heuristics for detecting and confirming successful submissions.
  - Richer semantics for restarting or resuming failed runs.

---

## Architectural Shifts

The original roadmap assumed that worker dispatch, FSM transitions, durable evidence tracking, and formal application packets were open development items. **These concepts are now fully implemented baseline architecture** and must be treated as established contracts, not future aspirations.

## Strategic Priorities for Future Hardening

1. **Adapter Breadth:** Expand field adapter coverage to confidently navigate a wider array of ATS controls and multi-page application patterns.
2. **Source Resiliency:** Deepen direct-site enrichment capabilities and introduce actionable source-health diagnostics.
3. **Quality of Match:** Strengthen the underlying quality of the scoring and tailoring algorithms, moving beyond basic keyword intersection.
4. **Operator Experience:** Improve the administrative and diagnostic surfaces, specifically regarding retry management, packet inspection, and failure analysis.
5. **Authentication Flows:** Finalize live provider verification and introduce richer, more resilient OAuth recovery flows for inbox integrations.

## Immutable Operational Guardrails

All future development must adhere to these core principles:
1. **The Canonical Profile is Absolute.** (The master record is the only source of truth).
2. **Tailoring May Not Invent Facts.** (Zero tolerance for generative hallucination).
3. **Risky Answers Require Approval.** (Unknowns and sensitive questions must be gated).
4. **Sensitive Data Must Be Masked.** (Tokens, OTPs, and PII must not leak into logs).
5. **Respect Anti-Bot Measures.** (Encountering CAPTCHAs must result in a graceful pause, never an attempt to bypass).
