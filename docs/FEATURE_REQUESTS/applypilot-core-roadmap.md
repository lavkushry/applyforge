# ApplyPilot-Core Roadmap Status

## Purpose

This document no longer functions as a greenfield feature request. Instead, it serves as a historical record detailing what ApplyForge has successfully implemented from the original ApplyPilot-style roadmap, while clearly outlining the remaining tasks.

The core target architecture remains unchanged across six phases:
1. Discover
2. Enrich
3. Score
4. Tailor
5. Prepare
6. Execute

The critical metric for this document is current status, not aspiration.

## Implementation Status

### 1. Discovery

**Implemented:**
- Role-driven source subscriptions.
- Packaged discovery presets and structured search templates.
- Discovery-first ingestion runs.
- Comprehensive feed events governing job lifecycles (discovered, enriched, score-changed, expired).
- Foundational, MVP-depth support for Greenhouse, Lever, Workday-style, and direct sources.

**Remaining Gaps:**
- Breadth of source coverage across minor ATS platforms.
- Comprehensive source-health diagnostics and alerting.
- Richer, more resilient direct-site extraction strategies.

### 2. Enrichment

**Implemented:**
- Strict decoupling of discovery and enrichment phases.
- Reliable worker-queued enrichment processing per job.
- Robust tracking of enrichment status, metadata, and revision history.
- Precise source snapshot artifact linkage.

**Remaining Gaps:**
- Higher quality structured extraction for complex descriptions.
- Explicit operator-visible retry and backoff details within the UI.
- More sophisticated extraction cascades to handle fallback logic.

### 3. Scoring

**Implemented:**
- Advanced role-aware scoring engine.
- Actionable recommendation outputs.
- Transparent reporting of strengths, missing skills, and detailed reasoning.
- Immutable score snapshots directly tied to specific enrichment revisions.

**Remaining Gaps:**
- Deeper ontology or semantic matching rather than pure keyword reliance.
- Tighter calibration on compensation and complex visa requirements.
- More granular advanced readiness scoring.

### 4. Tailoring

**Implemented:**
- Strictly fact-locked tailoring mechanics.
- Targeted emphasis of relevant skills, experience, and projects.
- Explicit diff metadata highlighting matched vs. uncovered requirements.
- Theme-aware resume generation versions.
- Automated cover-letter generation.

**Remaining Gaps:**
- More intelligent experience bullet ranking and selection.
- Reusable, multi-strategy resume families spanning multiple roles.
- Higher visual fidelity aligning the UI preview with the final PDF export.

### 5. Preparation

**Implemented:**
- Formal application packet generation preceding execution.
- Comprehensive preflight readiness checks.
- Resolved answers firmly attached to verifiable provenance.
- Clear packet summaries exposed within application UI surfaces.

**Remaining Gaps:**
- Deeper predictive capabilities for unsupported fields prior to runtime execution.
- Richer packet diagnostics surfaced within admin operator views.

### 6. Execution

**Implemented:**
- Seamless creation of queued runs via the API.
- Worker-backed processing for both enrichment and active application execution.
- Highly durable step logging throughout the run sequence.
- Screenshot persistence natively handled as uploaded file records.
- Anti-bot detection natively triggering a safe pause state.
- Assisted "pause-before-submit" mechanics.
- OTP retrieval natively treated as a first-class execution step.
- Formal Finite State Machine (FSM) transitions governing run lifecycles.
- Operator actions facilitating resumption of paused, failed, or uncertain runs.

**Remaining Gaps:**
- Broader field adapter coverage handling esoteric form controls.
- More robust navigation handling across complex, multi-page ATS flows.
- Stronger, deterministic submit confirmation heuristics.
- Richer semantic logic for restarting interrupted workflows.

## Architectural Baseline Shifts

The original roadmap assumed the following components were open, future challenges:
- Worker dispatch as the primary execution path.
- A formalized, persisted application packet model.
- Durable step evidence and artifact logging.
- Strict run status state transitions.

*These features are now successfully implemented and must be treated as foundational baseline architecture, not future development work.*

## Remaining Core Priorities

1. **Adapter Expansion:** Aggressively expand field adapter coverage to handle more diverse ATS controls and complex multi-page application patterns.
2. **Direct Extraction:** Significantly improve the depth of direct-site enrichment and the observability of source health.
3. **Engine Quality:** Elevate the qualitative depth of the scoring and tailoring engines, focusing on nuance rather than just operational breadth.
4. **Diagnostics UI:** Enhance admin and diagnostic surfaces to provide richer visibility into retries, packet contents, and execution failures.
5. **Provider Resilience:** Implement live provider verification alongside richer OAuth recovery flows for inbox integrations.

## Non-Negotiable Guardrails

These principles govern all past and future implementations:
1. The **Canonical Profile** remains strictly authoritative.
2. Tailoring mechanisms **may never invent facts**.
3. Risky or unknown application answers must always remain **approval-gated**.
4. Sensitive outputs, tokens, and codes must always remain **securely masked**.
5. Any CAPTCHA or anti-bot flows must **pause execution** rather than attempting evasion.
