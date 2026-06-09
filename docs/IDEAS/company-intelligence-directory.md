# Company Intelligence Directory: Implementation Status

## Overview

The concept of a Company Intelligence Directory has transitioned from a proposed idea to an implemented foundational feature within ApplyForge.

The system now actively maintains a graph of user-scoped company entities, linking job postings to specific organizations rather than relying solely on raw text strings.

## Current Capabilities

### Database Architecture
The following tables have been established:
- `companies`: The core entity representing an organization.
- `company_career_portals`: Tracks metadata specific to the employer's ATS or career site.
- `company_contacts`: Stores recruiter or HR contact information associated with the company.

### API Surface
The backend provides full CRUD operations for company management:
- `GET /companies`: Retrieve the user's company directory.
- `POST /companies`: Register a new company.
- `GET /companies/{company_id}`: Fetch detailed company intelligence.
- `PUT /companies/{company_id}`: Update company information.
- Operations for creating portals and contacts are nested within this route group.

### User Interface
The Next.js frontend now includes:
- A dedicated directory view listing all recognized companies.
- Workflows for manually creating companies, career portals, and specific recruiter contacts.
- UI elements linking specific job postings to their parent company records.

### System Integration
Company resolution is actively woven into core workflows:
- Jobs added manually can be explicitly linked to a known `company_id`.
- The automated ingestion engine utilizes heuristics (matching normalized company names, portal URLs, and hostnames) to resolve scraped jobs to existing company records.
- Companies act as an intermediate intelligence layer between raw source discovery and the final job record.

## Remaining Development Tasks

While the foundation is solid, several advanced features remain pending:

1. **Deduplication Workflows:** Develop administrative tools allowing users to review and merge duplicate company profiles.
2. **Portal Diagnostics:** Implement automated health checks for recognized career portals to detect when a company changes its ATS provider.
3. **Resolution Heuristics:** Enhance the confidence scoring algorithm for automated job-to-company mapping and provide a clearer UI for users to override incorrect matches.
4. **Recruiter Metadata:** Expand the data model to capture richer source information regarding recruiter outreach and verification workflows.
5. **Operator Dashboards:** Build queue management screens to help operators manually resolve pending or low-confidence company matches.

## Strategic Importance

The company intelligence layer is a critical leverage point for the system's future evolution. It provides the necessary structure for:
- Improving the accuracy of source resolution during job scraping.
- Significantly enhancing the quality of job deduplication.
- Powering future workflows tailored specifically for interacting with recruiters.
- Allowing users to set automation preferences at the company level (e.g., "Auto-apply to all Engineering roles at Company X").
- Generating clearer diagnostic reports regarding which sources yield the most viable jobs.

## Development Directives

Any future enhancements must build upon this existing company graph structure. Do not architect parallel or redundant models for representing employers.
