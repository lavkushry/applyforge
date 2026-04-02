# Hardening and Roadmap TODOs

This document tracks the technical debt, feature enhancements, and hardening steps required following the successful implementation of the resume-template, company-directory, preference-export, and FSM initiatives.

## Platform Infrastructure
- [ ] **Database Migrations:** Deprecate the runtime `create_all` implementation in favor of strictly authored, Alembic-managed migrations.
- [ ] **Object Storage:** Implement an S3-compatible storage adapter to handle artifacts and uploads, including support for securely signed downloads.
- [ ] **Real-Time Updates:** Transition from long-polling to WebSockets or Server-Sent Events (SSE) to broadcast status updates for long-running worker tasks.

## Authentication and Security
- [ ] **Session Management:** Upgrade the current basic cookie session implementation to a robust architecture utilizing refresh-token rotation and strict session invalidation policies.
- [ ] **Authorization:** Introduce granular, per-route Role-Based Access Control (RBAC) to support upcoming multi-user and agency-level workflows.
- [ ] **Data Encryption:** Implement encryption-at-rest for sensitive profile answers and credentials, mitigating the risk of storing preferences as plain JSON.
- [ ] **Rate Limiting:** Expand rate-limiting middleware beyond authentication and inbox routes to comprehensively cover all write-heavy automation endpoints.

## Resume and Document Systems
- [ ] **Advanced Strategies:** Support the creation and management of multiple, distinct resume strategies and reusable variants categorized by role family.
- [ ] **Renderer Validation:** Finalize live production validation for the RenderCV pipeline and establish explicit artifact retention policies.
- [ ] **Preview Fidelity:** Enhance the web preview rendering engine to more accurately reflect the final, exported PDF artifacts.
- [ ] **Expanded Theming:** Introduce advanced LaTeX or Typst-grade theme support while strictly maintaining ATS-safe fallback defaults.

## Discovery and Enrichment Engines
- [ ] **Direct Page Extraction:** Build richer, more resilient extraction logic for proprietary company career sites and Workday-style portals.
- [ ] **Source Observability:** Develop comprehensive source-health diagnostics, including retry visibility metrics and automated alerts for stale or unresponsive sources.
- [ ] **Source Expansion:** Broaden ingestion coverage across new platforms while rigorously maintaining existing ATS-first deduplication and freshness constraints.
- [ ] **Retry Semantics:** Implement intelligent, per-source retry histories and backoff strategies, moving beyond simple manual enrichment retries.

## Company Intelligence
- [ ] **Data Integrity:** Develop administrative tooling to merge, review, and deduplicate overlapping company intelligence records.
- [ ] **Portal Health:** Introduce automated health checks and diagnostic reporting for integrated company career portals.
- [ ] **Resolution Overrides:** Improve the confidence scoring for job-to-company resolutions and provide a clearer UX for manual user overrides.

## Application Automation
- [ ] **Adapter Expansion:** Broaden the library of generic Playwright field adapters to support complex file variants, address composites, and advanced site-specific UI controls.
- [ ] **Checkpoint Recovery:** Implement robust "resume-from-checkpoint" semantics, allowing users to seamlessly restart partially failed or manually paused application runs.
- [ ] **Site-Specific Resiliency:** Develop broader, site-specific interaction adapters while ensuring the system gracefully degrades to manual intervention rather than failing entirely.

## Inbox and OAuth Integrations
- [ ] **Live Verification:** Execute and finalize live, end-to-end verification of the Gmail and Outlook OAuth flows against production credentials.
- [ ] **Token Lifecycle:** Implement token refresh telemetry, proactive re-authentication prompts, and clear UX flows for recovering revoked credentials.
- [ ] **Integration Testing:** Write provider-specific test suites verifying refresh-token rotation and graceful handling of `invalid_grant` errors.
- [ ] **Auditability:** Surface detailed connection audit histories and explicit "revoke access" controls within the user diagnostics panel.

## Diagnostics and Administration
- [ ] **Admin UX:** Expand the internal administrative interfaces to support efficient screenshot browsing, queue depth monitoring, and granular source-health drilldowns.
- [ ] **Search and Filtering:** Implement advanced search and filtering capabilities across the application run history, feed events, and OTP retrieval logs.

## Quality Assurance and CI/CD
- [ ] **Backend Integration:** Author comprehensive integration test suites covering authentication, job ingestion, resume parsing, and document export.
- [ ] **Frontend E2E:** Introduce Playwright End-to-End (E2E) coverage validating critical user journeys: sign-in, profile editing, job scoring, and resume parsing.
- [ ] **Automation E2E:** Develop specialized Playwright E2E tests validating the inbox OAuth connection flow and OTP-assisted application pause gates.
- [ ] **CI Pipelines:** Establish robust Continuous Integration workflows enforcing Python linting/testing and Web linting/building/type-checking on all Pull Requests.
