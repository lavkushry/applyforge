# Company Intelligence Directory Status

## Executive Summary

The Company Intelligence Directory has transitioned from a conceptual feature request to a core, implemented architectural foundation within ApplyForge.

The system now actively maintains a user-scoped company graph that acts as an intermediary layer between raw job ingestion and processed job records, providing crucial structure for source resolution, career portal tracking, and recruiter context.

## Current Implementation Status

### Data Model Foundations
The foundational schema is fully implemented and operational:
- `companies`: The canonical identity record for a specific employer.
- `company_career_portals`: Provider-specific metadata for direct integration and ATS tracking.
- `company_contacts`: Storage for recruiter and HR context, maintained independently of specific job requisitions.

### API Capabilities
The backend fully supports the company intelligence domain:
- Standard CRUD operations (`GET /companies`, `POST /companies`, `GET /companies/{id}`, `PUT /companies/{id}`).
- Dedicated sub-routes for portal and contact creation/listing within the company route grouping.

### User Interface Integration
The web frontend currently supports:
- An internal company directory listing.
- Company creation and editing flows.
- Career portal and recruiter contact management.
- Visibility into linked jobs directly from the company detail view.

### Pipeline Integration
Company intelligence is actively wired into the broader data pipeline:
- **Manual Creation:** Users can explicitly resolve manually added jobs to a known `company_id`.
- **Automated Ingestion:** The discovery pipeline attempts heuristic company resolution utilizing normalized company names, parsed hostnames, and known portal metadata.

## Strategic Roadmap and Next Steps

While the foundation is secure, the intelligence directory requires further hardening to maximize its leverage across the platform:

1. **Data Integrity Tooling:** Develop administrative workflows to merge overlapping company records and resolve duplicate entries gracefully.
2. **Portal Observability:** Implement automated health checks, uptime tracking, and diagnostic reporting specifically for integrated career portals.
3. **Resolution Confidence:** Refine the heuristic algorithms for job-to-company resolution, surface confidence scores in the UI, and provide a clearer user experience for manual overrides.
4. **Contact Verification:** Enrich the recruiter contact model with stronger source provenance metadata and formal verification workflows.
5. **Operator Workflows:** Create dedicated administrative queues for reviewing and resolving unmatched or low-confidence company entities discovered during ingestion.

## Value Proposition

Maturing the Company Intelligence Directory remains a high-priority investment. A robust company graph directly enables:

- Higher fidelity source resolution and deduplication quality.
- The foundation for future recruiter-aware application workflows.
- Granular, company-level automation policies (e.g., "Always pause automation for Company X").
- Clearer diagnostics regarding ATS health and source reliability.

## Implementation Guidance

**Core Directive:** Future enhancements to employer tracking or job grouping must extend this existing company graph. You must not introduce parallel or competing company data models.
