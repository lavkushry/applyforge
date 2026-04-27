# Company Intelligence Directory Status

## Current Implementation Status

This feature is no longer in the ideation phase; the foundational architecture has been successfully implemented within ApplyForge.

The system now actively supports:
*   User-scoped `companies`.
*   Associated `company_career_portals`.
*   Associated `company_contacts`.
*   Comprehensive CRUD routing for company entities.
*   A lightweight internal company directory interface.
*   Job-to-company resolution hooks integrated into both manual creation and automated discovery flows.

## Shipped Capabilities

### Data Model
The following relational tables are deployed and active:
*   `companies`
*   `company_career_portals`
*   `company_contacts`

### API Layer
The following endpoints are functional:
*   `GET /companies`
*   `POST /companies`
*   `GET /companies/{company_id}`
*   `PUT /companies/{company_id}`
*   Nested workflows for creating and listing portals and contacts within the company route group.

### Web Interface
The frontend currently provides UI components for:
*   Viewing the company list.
*   Creating new companies, portals, and contacts.
*   Selecting companies from dropdowns.
*   Viewing job listings linked to specific companies.

### Core Integration
The core application logic leverages the company directory by:
*   Resolving manually created jobs to a specific `company_id`.
*   Executing automated resolution during job ingestion, utilizing normalized company names alongside portal or hostname hints to match discovered jobs to existing company records.
*   Positioning company records as a critical intelligence layer between raw source discovery and formalized job records.

## Remaining Development Work

While the foundation is solid, the following enhancements are required to fully realize the company intelligence directory:

1.  **Duplicate Management**: Develop administrative tooling and workflows to identify, review, and merge duplicate company records.
2.  **Portal Health Monitoring**: Implement automated health checks and diagnostic reporting for tracked `company_career_portals`.
3.  **Resolution Confidence**: Improve job-to-company matching algorithms by exposing confidence scores and providing an intuitive UI for manual user overrides.
4.  **Recruiter Metadata**: Enhance the system's ability to capture and verify richer recruiter and source metadata.
5.  **Operator Tooling**: Build dedicated administrative interfaces for managing review queues and resolving unmatched company data.

## Strategic Importance

The company intelligence directory is a critical leverage point for future platform capabilities, specifically enabling:

*   Higher accuracy in source resolution and data extraction.
*   Superior deduplication quality during high-volume job ingestion.
*   The foundation for future recruiter-aware application workflows.
*   The ability to set automation preferences at the company level.
*   Clearer, more actionable diagnostics regarding job sources.

## Implementation Guidance

Future development should focus on extending and enriching the existing company graph (e.g., adding deeper metadata, improving resolution heuristics) rather than attempting to build a parallel or competing company data model.
