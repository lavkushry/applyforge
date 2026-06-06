# ApplyPilot-Core Roadmap Status

## Overview
This document tracks the realized ApplyPilot-style implementations against the aspirational roadmap. The system operates on six primary steps: Discover, Enrich, Score, Tailor, Prepare, and Execute.

## Component Statuses

### 1. Discovery
**Done**: Custom role feeds, scheduled source discovery runs, Greenhouse/Lever base coverage.
**Todo**: Expanded source integrations, real-time health diagnostics, complex direct-site extractors.

### 2. Enrichment
**Done**: Worker-queued separation of discovery versus enrichment, revision snapshots.
**Todo**: Cascading extraction structures, refined operator retry UX.

### 3. Scoring
**Done**: Role-centric matching logic mapping strengths and missing requirements.
**Todo**: Advanced visa, compensation calibrations, and deeper semantic evaluations.

### 4. Tailoring
**Done**: Fact-locked generative diffs, ATS-theme variants, cover letter generation.
**Todo**: Stronger AI bullet point ordering and multi-strategy tracking frameworks.

### 5. Preparation
**Done**: Preflight packet readiness hooks mapping resolved questions.
**Todo**: More aggressive pre-runtime detection of unsupported form fields.

### 6. Execution
**Done**: Queued worker tasks, FSM mapping, anti-bot checkpoints, OTP interception, snapshot persistence.
**Todo**: More robust multi-page ATS navigators and submit-confirmation detection heuristics.

## Strategic Priority
What was once future work (Playwright integration, queued execution, application packet prep) is now foundational architecture. The primary target moves to expanding the field adapter capabilities, improving direct site handling, and securing OAuth recovery logic.

**Strict Guardrails**: Tailoring must never hallucinate profile data. Bots are not to be aggressively bypassed. Secret masking is required at all levels.