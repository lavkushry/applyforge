# Feature Request: ApplyPilot-Core Roadmap for ApplyForge

## Summary

This document proposes how to evolve ApplyForge into an ApplyPilot-style core product while preserving ApplyForge's existing strengths:

- canonical fact-locked candidate profile,
- role-driven job discovery and scoring,
- inspectable automation runs,
- approval gates for risky answers,
- OTP and diagnostics support.

The goal is **not** to clone another project blindly. The goal is to make ApplyForge's core product a full pipeline:

1. discover,
2. enrich,
3. score,
4. tailor,
5. generate cover letter,
6. execute application workflow.

## Why this feature request exists

ApplyForge already has important building blocks across these stages, but the current implementation is uneven:

- discovery exists but source coverage is still narrow,
- enrichment is minimal,
- scoring exists but remains heuristic and shallow,
- tailoring exists but is still basic,
- application execution is persisted nicely but still behaves like a skeleton rather than a complete browser-driven pipeline,
- worker execution exists but is not yet the main run path.

This feature request turns that gap into a concrete roadmap.

## What ApplyForge already has

### 1. Candidate brain and durable data model

Current schema already includes:

- canonical candidate profile data,
- resumes and tailored resume versions,
- jobs and job scores,
- target roles and target role sources,
- job ingestion runs and job feed events,
- applications, application runs, and application steps,
- uploaded files,
- inbox connections and OTP events.

This is already a strong foundation for a 6-stage application pipeline.

## Evidence from current implementation

### Discovery and feed

`apps/api/app/services/role_ingestion.py` already supports role-driven ingestion and persistence of discovery events.

### Scoring

`apps/api/app/services/scoring.py` already computes job fit, strengths, missing skills, and recommendation text.

### Tailoring and cover letters

`apps/api/app/services/tailor.py` already supports ranked skills, fact-preserving tailored resume content, risky question detection, and common answer generation.

### Job routes

`apps/api/app/api/routes/jobs.py` already supports manual import, feed retrieval, scoring, tailoring, eligibility checks, and cover-letter generation.

### Application workflow

`apps/api/app/api/routes/applications.py` already supports application preparation, assisted runs, auto runs, and OTP retrieval.

### Worker and browser execution

`apps/worker/app/playwright_runner.py` already opens pages, fills very basic fields, captures screenshots, and pauses before submit.

## Deep gap analysis

### Stage 1: Discover

### What is already implemented

- role-based source configuration through `target_role_sources`
- ingestion runs through `job_ingestion_runs`
- feed events through `job_feed_events`
- source adapters for:
  - Greenhouse boards
  - Lever boards
  - direct URL fetch

### What is missing

- much broader source coverage
- source-health tracking beyond pass/fail message storage
- richer direct site extraction
- URL import that resolves real application pages more intelligently
- better handling for disappeared or stale jobs across source sweeps
- future-ready separation of:
  - discovery signals
  - canonical application endpoints

### Why this matters

If ApplyForge is going to adopt an ApplyPilot-style core, discovery must become a proper subsystem rather than a few adapters.

## Stage 2: Enrich

### What is already implemented

- jobs are normalized before insertion
- descriptions and source metadata are stored

### What is missing

- dedicated enrichment pipeline stage
- job page fetching separate from discovery
- structured description extraction cascade
- normalized extraction confidence
- extracted sections such as responsibilities, requirements, seniority hints, visa hints, salary hints, and ATS clues
- storage of raw job document snapshots for debugging and reprocessing

### Why this matters

Right now discovery and enrichment are effectively compressed into one lightweight step. A serious apply pipeline needs enrichment as its own repeatable stage.

## Stage 3: Score

### What is already implemented

- overall score
- strengths
- missing skills
- recommendation
- role-aware scoring inputs

### What is missing

- richer skill ontology and parsing
- stronger location / compensation / visa weighting
- score calibration and explainability beyond keyword presence
- separate score dimensions for:
  - must-have match
  - nice-to-have match
  - role-title fit
  - location fit
  - compensation fit
  - application readiness
- score snapshots tied to enrichment revisions

### Why this matters

The current scoring engine is a good MVP, but it is still mostly a lightweight heuristic model. If the project core becomes an apply pipeline, the scoring layer must better decide what should proceed to tailoring and automation.

## Stage 4: Tailor

### What is already implemented

- tailored resume versions are stored
- skills can be reordered based on job text
- summary is adjusted toward role intent
- fact-locked sections are preserved
- cover letters are generated and stored

### What is missing

- stronger bullet selection and reordering for experience
- tailored project emphasis
- deeper structured diffs between source and tailored resume
- better preview fidelity versus exported artifact
- stronger validation that tailored content remains factual
- reusable resume strategies by role family

### Why this matters

To support ApplyPilot-style throughput, the tailoring stage must become more deterministic, higher quality, and easier to inspect.

## Stage 5: Application preparation

### What is already implemented

- `Application` records can be prepared per job
- applications move into `ready_to_apply`
- eligibility checks exist per role threshold
- answer generation exists for common questions

### What is missing

- a formal "application packet" or prep artifact containing:
  - selected resume version
  - cover letter
  - resolved candidate answers
  - required documents
  - detected risks
- per-job preflight validation before the browser opens
- unsupported-field prediction before runtime

### Why this matters

A reliable apply engine should prepare all assets first, then execute with fewer surprises.

## Stage 6: Apply execution

### What is already implemented

- application runs and step rows are durable
- assisted and auto modes exist
- approval gates exist
- OTP lookup is modeled as a first-class step
- Playwright worker exists
- screenshots exist at the worker level

### What is missing

- API dispatch into worker as the default execution path
- callback or polling path to persist worker step outputs back into `application_steps`
- support for:
  - dropdowns
  - radios
  - checkboxes
  - file uploads
  - multi-page forms
  - conditional questions
  - resume/resume-from-last-step behavior
- clear submit confirmation detection
- real screenshot ingestion into `uploaded_files`
- external task state and retries bound to `external_task_id`
- structured field adapter registry by ATS / site type

### Why this matters

This is the single biggest gap between current ApplyForge and an ApplyPilot-style core. The current implementation stores the run well, but the real browser execution path is still too thin.

## Current implementation constraints that should be preserved

This roadmap should preserve the product rules already established in ApplyForge:

1. canonical profile remains authoritative,
2. tailoring may optimize phrasing but not invent facts,
3. risky questions must remain approval-gated,
4. automation runs must remain inspectable after partial failure,
5. OTP and sensitive outputs must remain masked,
6. unsupported or anti-bot-protected steps should fail gracefully.

## Proposed roadmap

## Milestone 1: Make the apply engine real

### Goal

Turn current skeleton logging into real async browser-backed execution.

### Deliverables

- dispatch `run-assisted` and `run-auto` into worker tasks
- persist worker step results into `application_steps`
- persist screenshots into `uploaded_files`
- store browser worker task IDs in `external_task_id`
- add run status transitions for queued, running, paused, failed, completed, uncertain

### Acceptance criteria

- assisted apply uses the worker by default
- run timeline reflects real worker steps
- screenshots can be viewed from the run history
- pause-before-submit still works

## Milestone 2: Add field adapter registry

### Goal

Support common ATS controls with reusable adapters.

### Deliverables

- field adapters for text, textarea, select, radio, checkbox, file upload
- answer resolution pipeline from `saved_answers`, `preferences`, and tailored resume assets
- unsupported-field capture in step output

### Acceptance criteria

- common ATS forms can be partially or mostly completed without site-specific one-offs
- unsupported controls pause the run with evidence

## Milestone 3: Separate discover and enrich

### Goal

Make discovery broad and enrichment reliable.

### Deliverables

- split source discovery from full job-detail enrichment
- add enrichment status and failure metadata
- add richer extraction for direct career pages
- add source-health diagnostics

### Acceptance criteria

- newly discovered jobs can be enriched after discovery
- failed extraction does not block the entire discovery run
- users can see what was discovered but not yet fully enriched

## Milestone 4: Strengthen scoring and tailoring

### Goal

Make pipeline decisions more trustworthy.

### Deliverables

- stronger score components and exposed explanations
- more structured resume diff metadata
- better tailored bullet selection and ranking
- reusable resume strategies by role family

### Acceptance criteria

- score explanations are more actionable
- tailored resumes show clearer job-specific improvements without invented claims

## Milestone 5: Application packet and preflight

### Goal

Prepare everything before execution.

### Deliverables

- preflight packet generation per job
- resolved selected resume version
- linked cover letter
- resolved application answers
- risk summary
- upload readiness checks

### Acceptance criteria

- apply runs begin from a prepared packet rather than ad hoc runtime lookups
- missing answers are flagged before the browser opens

## Schema changes recommended

### High priority

- add `application_packet_id` or `prepared_payload` to `application_runs`
- add richer status fields for jobs and applications
- add artifact linkage between worker outputs and uploaded files
- add enrichment status and enrichment metadata to jobs
- add worker callback-safe event persistence model if needed

### Medium priority

- add field-level answer provenance metadata
- add run restart checkpoints
- add submit confirmation evidence fields

## Engineering priority order

1. real worker dispatch and run persistence
2. field adapter registry
3. application packet / preflight layer
4. enrichment stage separation
5. stronger scoring and tailoring

## What should not happen

- do not replace durable run evidence with opaque automation
- do not let resume tailoring fabricate claims
- do not make risky answers silent defaults
- do not collapse discovery, enrichment, scoring, and apply into one non-debuggable step
- do not ship mass autonomy before the run model becomes trustworthy

## Suggested implementation entry points

- `apps/api/app/api/routes/applications.py`
- `apps/api/app/automation/engine.py`
- `apps/worker/app/playwright_runner.py`
- `apps/worker/app/tasks.py`
- `apps/api/app/services/role_ingestion.py`
- `apps/api/app/services/scoring.py`
- `apps/api/app/services/tailor.py`
- `apps/api/app/models/entities.py`

## Final recommendation

ApplyForge already has enough architecture to become an ApplyPilot-core product, but it should do so in this sequence:

- make execution real,
- make execution inspectable,
- improve source and enrichment depth,
- then scale source breadth and automation power.

That path preserves ApplyForge's strongest advantage: a trustworthy application operating system instead of a black-box mass apply bot.
