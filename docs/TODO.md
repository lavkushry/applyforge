# ApplyForge TODO & Next Hardening Steps

This document tracks the remaining tasks and hardening efforts required following the implementation of resume templates, the company directory, preference exports, and the application Finite State Machine (FSM).

## Platform Infrastructure
- [ ] **Database Migrations**: Fully transition from runtime `create_all` to strict Alembic-managed migrations for all schema evolutions.
- [ ] **Object Storage**: Implement an S3-compatible storage adapter to replace local disk storage, including support for securely signed downloads.
- [ ] **Realtime Updates**: Replace frontend polling with WebSockets or Server-Sent Events (SSE) to provide realtime updates for long-running application tasks.

## Authentication & Security
- [ ] **Session Management**: Upgrade the basic cookie session flow to incorporate refresh-token rotation and stricter expiration policies.
- [ ] **Authorization Layers**: Implement granular, per-route authorization controls to support future enterprise features like multi-user accounts and agency roles.
- [ ] **Data Encryption**: Implement encryption at rest for sensitive profile answers and user preferences (currently stored as plaintext JSON).
- [ ] **Rate Limiting**: Expand rate limiting controls beyond authentication and inbox routes to cover write-heavy automation endpoints.

## Document Processing & Resumes
- [ ] **Resume Strategies**: Introduce support for multiple resume strategies, enabling reusable, tailored variants categorized by role family.
- [ ] **RenderCV Hardening**: Finalize live RenderCV production validation and establish artifact retention policies.
- [ ] **Preview Fidelity**: Enhance the web UI preview engine to more accurately reflect the final, exported PDF artifacts.
- [ ] **Advanced Themes**: Introduce robust support for advanced LaTeX or Typst-grade themes while maintaining strict ATS-compatibility standards.

## Discovery & Data Enrichment
- [ ] **Direct Extraction**: Improve direct-page extraction capabilities specifically for company career sites and Workday-powered portals.
- [ ] **Source Observability**: Implement source-health diagnostics, granular retry visibility, and alerts for stale or failing data sources.
- [ ] **Coverage Expansion**: Broaden job source coverage while strictly adhering to ATS-first deduplication and data freshness requirements.
- [ ] **Advanced Retries**: Develop a robust per-source retry history and alerting mechanism, reducing reliance on manual enrichment retries.

## Company Intelligence
- [ ] **Data Deduplication**: Develop administrative tooling to merge and review duplicate company records.
- [ ] **Portal Health**: Implement automated health checks and specific diagnostics for tracked company career portals.
- [ ] **Resolution Confidence**: Enhance job-to-company resolution algorithms by adding confidence scoring and intuitive user override interfaces.

## Application Automation
- [ ] **Field Adapters**: Expand generic Playwright field adapters to handle file upload variants, composite address fields, and complex site-specific controls.
- [ ] **Checkpoint Resumption**: Improve "resume-from-last-checkpoint" semantics allowing graceful recovery of partially completed automation runs.
- [ ] **Fallback Mechanisms**: Increase coverage of site-specific adapters while ensuring graceful degradation to manual review states.

## Inbox & OAuth Integration
- [ ] **Live Verification**: Complete comprehensive end-to-end verification of Gmail and Outlook OAuth flows using production credentials.
- [ ] **Token Telemetry**: Implement robust telemetry for token refresh cycles, proactive re-authorization prompts, and user-friendly credential recovery UX.
- [ ] **Provider Testing**: Add specific test coverage for provider-dependent edge cases, including refresh-token rotation and invalid-grant exception handling.
- [ ] **Audit Controls**: Expose connection audit histories and explicit "revoke-access" controls within the diagnostics UI.

## Diagnostics & Administration
- [ ] **Admin Dashboards**: Expand the internal administrative surface to include centralized screenshot browsing, worker queue depth monitoring, and source-health drilldowns.
- [ ] **Advanced Filtering**: Enhance search and filtering capabilities across historical application runs, job feed events, and OTP interception logs.

## Quality Assurance & Testing
- [ ] **Integration Tests**: Expand integration test coverage for authentication flows, job ingestion, resume parsing, and document export pipelines.
- [ ] **E2E UI Testing**: Introduce Playwright End-to-End coverage for critical user journeys (sign-in, profile editing, job scoring, resume parsing).
- [ ] **E2E Automation Testing**: Add Playwright End-to-End coverage for complex flows including inbox OAuth connection and OTP-assisted application pauses.
- [ ] **CI Pipeline**: Implement a comprehensive Continuous Integration (CI) pipeline encompassing Python linting/testing and Web linting/building/typechecking.
