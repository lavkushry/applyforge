# Company Intelligence Directory Status

## Summary

The Company Intelligence Directory has successfully transitioned from an initial concept into a foundational implemented feature.

**ApplyForge currently supports:**
- Fully user-scoped `companies` tables.
- `company_career_portals` linking portals to parent companies.
- `company_contacts` securely tracking HR and recruiter profiles.
- Comprehensive CRUD API routes for company management.
- A streamlined, internal company directory UI page.
- Automated job-to-company resolution hooks seamlessly integrated into both manual creation and automated discovery flows.

## What is Already Shipped

### Data Model
The underlying database schema is active and supports:
- `companies`
- `company_career_portals`
- `company_contacts`

### API Architecture
The following core routes are operational:
- `GET /companies`
- `POST /companies`
- `GET /companies/{company_id}`
- `PUT /companies/{company_id}`
- Nested portal and contact creation/listing flows securely routed through the main companies group.

### Web Interface
The frontend successfully implements:
- Comprehensive company listing views.
- Streamlined company creation flows.
- Intuitive company selection mechanisms.
- Portal and contact creation interfaces.
- Clear visibility linking job records to their respective companies.

### Core Integration
System behavior actively leverages the directory:
- Manual job creation intuitively resolves and maps to a `company_id`.
- Automated ingestion proactively attempts company resolution by analyzing normalized company names against existing portal or hostname hints.
- Company records actively sit as an intermediate, structured layer between raw source discovery and finalized job records.

## What Remains

To fully realize the directory's potential, the following hardening steps are required:
1. **Data Integrity Tooling:** Implement operator tools specifically for merging duplicate company records and handling review queues.
2. **Portal Observability:** Introduce active health checks and dedicated diagnostic panels for career portals.
3. **Resolution Heuristics:** Enhance the confidence scoring for automated company resolution and provide a clearer user override UX.
4. **Recruiter Metadata:** Expand the data model to accommodate richer recruiter-source metadata, accompanied by proper verification workflows.
5. **Operator Queues:** Build operator interfaces to easily surface and manually link unresolved or ambiguous company matches.

## Why This Still Matters

Despite the foundation being fully shipped, company intelligence remains a critical leverage point for future scaling:
- It fundamentally drives **better source resolution**.
- It guarantees **stronger deduplication quality** across disparate ingestion sources.
- It paves the way for advanced **recruiter-aware workflows**.
- It inherently supports broad, **company-level automation preferences**.
- It ensures significantly **clearer job-source diagnostics** for operators.

## Current Guidance

*Architectural Directive:* All future development must extend and enrich the existing company graph. Do not attempt to build parallel, redundant company models.
