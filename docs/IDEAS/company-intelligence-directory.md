<!-- REWRITTEN DOCUMENT: company-intelligence-directory.md -->
<!-- This document has been comprehensively reviewed and rewritten for clarity and consistency. -->

# Company Intelligence Directory Status

## Section: Summary

This is no longer just an idea. The foundation is implemented.

ApplyForge now has:

- user-scoped `companies`
- `company_career_portals`
- `company_contacts`
- company Create, Read, Update, Delete routes
- a thin internal company directory page
- job-to-company resolution hooks in manual creation and discovery flows

## Section: What is already shipped

### Data model

Implemented tables:

- `companies`
- `company_career_portals`
- `company_contacts`

### API

Implemented routes:

- `GET /companies`
- `POST /companies`
- `GET /companies/{company_id}`
- `PUT /companies/{company_id}`
- portal and contact create/list flows through the companies route group

### Web

Implemented UI:

- company list
- company create flow
- company selection
- portal creation
- contact creation
- linked job visibility

### Integration

Implemented behavior:

- manual job creation can resolve to `company_id`
- ingestion attempts company resolution from normalized company names and portal or hostname hints
- company records sit between source discovery and job records

## Section: What remains

1. Add merge and duplicate-review tooling for company records.
2. Add portal health checks and diagnostics.
3. Add better confidence scoring and override UX for company resolution.
4. Add richer recruiter-source metadata and verification workflows.
5. Add operator tooling for review queues and unresolved company matches.

## Section: Why this still matters

Even though the foundation is shipped, company intelligence remains a major leverage point for:

- better source resolution
- stronger dedupe quality
- future recruiter-aware workflows
- company-level automation preferences
- clearer job-source diagnostics

## Section: Current guidance

Future work should extend the existing company graph rather than building a parallel company model.
