# ApplyPilot-Core Roadmap Status

## 🎯 Purpose

This document is no longer a proposal for a greenfield feature request. Instead, it serves as the definitive status record tracking what ApplyForge has successfully implemented from the original ApplyPilot-style product roadmap, and what specific hardening tasks remain.

The core target architecture remains unchanged across six fundamental stages:
1. **Discover**
2. **Enrich**
3. **Score**
4. **Tailor**
5. **Prepare**
6. **Execute**

The focus of this document is explicitly on *status*, not aspiration.

---

## ✅ Implemented vs. Pending

### 1. Discovery
**Implemented:**
- Role-driven source subscriptions.
- Packaged discovery presets and advanced search templates.
- Discovery-first asynchronous ingestion runs.
- Comprehensive feed events (`discovered`, `enriched`, `score_changed`, `expired`).
- Foundational MVP support for major ATS platforms (Greenhouse, Lever, Workday-style, direct-source).

**Still Thin (Pending Hardening):**
- Breadth of source coverage requires expansion.
- Source-health diagnostics and alerting.
- Richer direct-site extraction strategies.

### 2. Enrichment
**Implemented:**
- Explicit architectural split between discovery and enrichment pipelines.
- Worker-queued, job-specific background enrichment.
- Tracking of enrichment status, metadata, and revision histories.
- Durable source snapshot artifact linkage.

**Still Thin (Pending Hardening):**
- Quality of deep, structured extraction needs refinement.
- Operator-visible retry and backoff details are lacking in the UI.
- More advanced extraction cascades and fallback heuristics.

### 3. Scoring
**Implemented:**
- Algorithmic scoring deeply aware of target role parameters.
- Final actionable recommendation outputs.
- Granular breakdown of strengths, missing skills, and explicit reasoning.
- Score snapshots tightly coupled to specific enrichment revisions.

**Still Thin (Pending Hardening):**
- Requires a stronger semantic ontology for matching logic.
- Improved calibration for complex compensation structures and visa requirements.
- Advanced, multi-variable readiness scoring.

### 4. Tailoring
**Implemented:**
- Strict, fact-locked tailoring constraints (Zero Hallucination Policy).
- Emphasized matching of skills, experience, and projects.
- Diff metadata highlighting matched vs. uncovered requirements.
- Theme-aware resume versions and exports.
- Automated cover-letter generation.

**Still Thin (Pending Hardening):**
- Experience bullet ranking needs stronger contextual relevance.
- Support for reusable, multi-strategy resume families.
- Higher visual fidelity matching between the web preview and final PDF export.

### 5. Preparation
**Implemented:**
- Generation of formalized application packets prior to execution.
- Comprehensive preflight readiness checks.
- Resolved answers firmly attached to data provenance.
- Clear packet summaries exposed in application UI surfaces.

**Still Thin (Pending Hardening):**
- Deeper predictive modeling to identify unsupported ATS fields *before* runtime execution begins.
- Richer, more actionable packet diagnostics in admin surfaces.

### 6. Execution
**Implemented:**
- API-driven queued run creation.
- Worker-backed background enrichment and dynamic application execution.
- Durable, granular step-by-step logging.
- Reliable screenshot persistence via the uploaded files architecture.
- Anti-bot detection resulting in graceful pause states.
- Assisted pause-before-submit gates for user verification.
- First-class run steps for Inbox OTP retrieval.
- Formal FSM (Finite State Machine) run transitions.
- Operator override actions for paused, failed, and uncertain runs.

**Still Thin (Pending Hardening):**
- Broadening field adapter coverage across complex, custom ATS elements.
- Robust handling of complex, multi-page ATS pagination flows.
- Stronger heuristics for verifying successful submit confirmations.
- Richer restart and resumption semantics for partially failed runs.

---

## 🔄 Roadmap Evolution

The original roadmap assumed several major architectural pillars were still open questions. Today, the following are fully present and must be treated as **baseline architecture**, not future work:
- Worker dispatch as the primary execution path.
- The persisted Application Packet model.
- Durable step evidence tracking (logs + screenshots).
- Formal FSM run status transitions.

---

## 🚀 Remaining Roadmap Priorities

Future sprint cycles must prioritize the following to finalize the core implementation:

1. **Adapter Expansion:** Broaden Playwright field adapter coverage across a wider array of ATS controls and multi-page form patterns.
2. **Deep Enrichment:** Improve direct-site enrichment depth and implement proactive source-health diagnostics.
3. **Evaluation Quality:** Strengthen the core quality of the semantic scoring and tailoring algorithms, moving beyond basic keyword breadth.
4. **Operator Tooling:** Improve administration and diagnostic surfaces, specifically concerning retries, packet inspection, and failure analysis.
5. **Live Integrations:** Conduct full live provider verification and build richer OAuth recovery and re-auth flows.

---

## 🛡️ Non-Negotiable Guardrails

As development continues, the following core constraints remain absolute:

1. **The Canonical Profile is Absolute.** It remains the authoritative source for all data.
2. **Zero Hallucination.** Tailoring algorithms may *not* invent facts.
3. **Approval Gates.** Risky or unknown application answers remain strictly approval-gated.
4. **Privacy Protection.** Sensitive outputs (Tokens, OTPs) remain aggressively masked.
5. **Respect Security.** CAPTCHA or anti-bot flows must *pause* execution rather than attempt to bypass the challenge.