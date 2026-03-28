# Starter Idea: Company Intelligence Directory

## Why this is the right next project

ApplyForge already has role-linked sources, job ingestion runs, normalized jobs, feed events, and scoring. What it does not yet have is a reusable company intelligence layer that sits between discovery and application.

That gap makes source expansion harder than it needs to be.

A contributor can create a shared directory of:

- companies,
- mapped career portals,
- recruiter and HR contacts,
- company-level discovery metadata.

This will make future job ingestion cleaner, improve dedupe quality, and reduce repeated work when the same company appears across multiple source surfaces.

## Product goal

Add a first-class company directory so ApplyForge can resolve and reuse:

1. company identity,
2. canonical careers URL,
3. structured portal type,
4. recruiter or HR contacts,
5. company-to-job relationships.

## Problem statement

Today, job sources are tied mostly to target roles and job records. That works for Greenhouse, Lever, and manual imports, but it becomes messy when the same company is discovered from multiple places.

Examples:

- a company has both a Greenhouse board and recruiter hiring posts,
- the same job is seen from a company careers page and a social post,
- HR contact details are found separately from the job source,
- future ingestion needs to resolve the real careers endpoint before creating jobs.

Without a company layer, normalization and source reuse become weaker over time.

## Scope for this starter task

This task should focus on the foundation only.

### In scope

- add SQLAlchemy models for a company directory foundation,
- add matching Pydantic schemas,
- add Alembic migration scaffold or model-side implementation note consistent with current repo state,
- add CRUD routes for companies,
- add CRUD routes for company career portals,
- add CRUD routes for company contacts,
- add a simple web page or admin surface to list and create companies,
- link jobs to `company_id` where feasible without breaking existing flows,
- keep company data user-scoped or global according to the chosen design, but document the decision clearly.

### Out of scope

- full LinkedIn-style scraping,
- CAPTCHA bypass,
- login-dependent scraping,
- stealth automation against protected sites,
- full contact enrichment pipelines,
- email sending or outreach automation,
- Workday or other complex portal parsers in this first pass.

## Proposed data model

### `companies`

Suggested fields:

- `id`
- `name`
- `normalized_name`
- `website_url`
- `careers_url`
- `linkedin_url`
- `hq_location`
- `industry`
- `notes`
- `active`
- timestamps

### `company_career_portals`

Suggested fields:

- `id`
- `company_id`
- `provider_kind` (`greenhouse`, `lever`, `ashby`, `workday`, `smartrecruiters`, `direct_site`)
- `base_url`
- `board_token`
- `health_status`
- `supports_structured_fetch`
- `last_checked_at`
- `notes`
- timestamps

### `company_contacts`

Suggested fields:

- `id`
- `company_id`
- `full_name`
- `title`
- `email`
- `linkedin_url`
- `contact_type` (`recruiter`, `hr`, `hiring_manager`, `referral`)
- `source`
- `source_url`
- `confidence`
- `last_verified_at`
- `notes`
- timestamps

## API shape

Suggested new route groups:

- `GET /companies`
- `POST /companies`
- `GET /companies/{company_id}`
- `PUT /companies/{company_id}`
- `GET /companies/{company_id}/portals`
- `POST /companies/{company_id}/portals`
- `GET /companies/{company_id}/contacts`
- `POST /companies/{company_id}/contacts`

Keep response shapes simple and consistent with the existing route style.

## UI shape

Start with one thin internal-facing page:

- company list,
- create company form,
- company detail card,
- related portals,
- related contacts.

This does not need polished CRM behavior yet.

## Integration expectations

A good first implementation should make it easier for future ingestion work to:

- resolve a company before inserting a job,
- attach a canonical careers source,
- preserve recruiter metadata separately from the job record,
- improve dedupe when the same company appears via multiple discovery paths.

Do not break current role-based ingestion.

## Acceptance criteria

1. A developer can create and list companies through the API.
2. A developer can add one or more career portals to a company.
3. A developer can add one or more recruiter or HR contacts to a company.
4. A basic web surface exists to inspect this data.
5. Existing job ingestion continues to work.
6. The implementation documents how future job sources should resolve through the company layer.

## Suggested files to inspect first

- `apps/api/app/models/entities.py`
- `apps/api/app/api/routes/roles.py`
- `apps/api/app/api/routes/jobs.py`
- `apps/api/app/services/role_ingestion.py`
- `apps/web/app/jobs/page.tsx`
- `docs/ARCHITECTURE.md`
- `docs/REQUIREMENTS.md`
- `docs/TODO.md`

## Engineering notes

- Follow the repo invariant that generated or discovered content must stay inspectable.
- Keep the implementation additive and low-risk.
- Prefer clean normalized records over trying to build a giant scraper first.
- If multi-user scoping is unclear, document the chosen assumption in the code or brief notes.

## What success looks like

After this task lands, ApplyForge should have the beginning of a reusable company graph.

That will make future work on job discovery, source resolution, dedupe, and recruiter-aware workflows much easier.
