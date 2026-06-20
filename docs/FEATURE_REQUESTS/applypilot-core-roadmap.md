<!-- REWRITTEN DOCUMENT: applypilot-core-roadmap.md -->
<!-- This document has been comprehensively reviewed and rewritten for clarity and consistency. -->

# ApplyPilot-Core Roadmap Status

## Section: Purpose

This document no longer describes a greenfield feature request. It now records what ApplyForge has already implemented from the ApplyPilot-style roadmap and what remains.

The target shape is still the same:

1. discover
2. enrich
3. score
4. tailor
5. prepare
6. execute

But the important question is now status, not aspiration.

## Section: Completed or largely completed

### 1. Discovery

Implemented:

- role-driven source subscriptions
- packaged discovery presets and search templates
- discovery-first ingestion runs
- feed events for discovered, enriched, score-changed, and expired jobs
- Greenhouse, Lever, Workday-style, and direct-source support at Minimum Viable Product depth

Still thin:

- source coverage breadth
- source-health diagnostics
- richer direct-site extraction

### 2. Enrichment

Implemented:

- explicit discovery -> enrichment split
- worker-queued enrichment per job
- enrichment status, metadata, and revision tracking
- source snapshot artifact linkage

Still thin:

- richer structured extraction quality
- operator-visible retry and backoff detail
- more advanced extraction cascades

### 3. Scoring

Implemented:

- role-aware scoring
- recommendation output
- strengths, missing skills, and reasons
- score snapshots tied to enrichment revisions

Still thin:

- stronger ontology or semantic matching
- better compensation and visa calibration
- more advanced readiness scoring

### 4. Tailoring

Implemented:

- fact-locked tailoring
- emphasized skills, experience, and projects
- diff metadata with matched and uncovered requirements
- theme-aware resume versions
- cover-letter generation

Still thin:

- stronger experience bullet ranking
- reusable multi-strategy resume families
- higher-fidelity preview versus final export

### 5. Preparation

Implemented:

- formal application packet generation
- preflight readiness checks
- resolved answers with provenance
- packet summary in application surfaces

Still thin:

- deeper unsupported-field prediction before runtime
- richer packet diagnostics in admin surfaces

### 6. Execution

Implemented:

- queued run creation through the API
- worker-backed enrichment and application execution
- durable step logging
- screenshot persistence through uploaded files
- anti-bot detection with pause
- assisted pause-before-submit
- OTP retrieval as a first-class run step
- formal run FSM transitions
- operator resume action for paused, failed, and uncertain runs

Still thin:

- broad field adapter coverage
- more robust multi-page ATS flows
- stronger submit confirmation heuristics
- richer restart semantics

## Section: What changed since the original roadmap

The original roadmap assumed these were still open:

- worker dispatch as the main run path
- persisted application packet model
- durable step evidence
- run status transitions

Those are now present and should be treated as baseline architecture, not future work.

## Section: Remaining roadmap priorities

1. Expand field adapter coverage across more ATS controls and multi-page patterns.
2. Improve direct-site enrichment depth and source-health diagnostics.
3. Strengthen scoring and tailoring quality, not just breadth.
4. Improve admin and diagnostics surfaces around retries, packets, and failures.
5. Add live provider verification and richer OAuth recovery flows.

## Section: Guardrails that remain non-negotiable

1. Canonical profile remains authoritative.
2. Tailoring may not invent facts.
3. Risky or unknown answers remain approval-gated.
4. Sensitive outputs remain masked.
5. CAPTCHA or anti-bot flows pause rather than bypass.
