# TODO / Next Hardening Steps

This document explicitly tracks the remaining engineering priorities following the successful delivery of resume-templates, company-directory, preference-export, and application FSM capabilities.

## 1. Platform Infrastructure

- **Database Migrations:** Completely deprecate runtime `create_all` commands, migrating strictly to Alembic-managed schema revisions.
- **Durable Storage:** Implement an S3-compatible storage adapter to securely manage artifact persistence and signed downloads.
- **Run Telemetry:** Transition long-running application run updates from polling mechanisms to webhook or stream-based updates.

## 2. Authentication and Security

- **Session Hardening:** Replace the MVP basic cookie session flow with robust refresh-token rotation and stricter session lifetime policies.
- **Authorization Policies:** Introduce granular, per-route authorization layers to facilitate forthcoming multi-user and agency roles.
- **Data Encryption:** Encrypt sensitive profile answers and automation preferences at rest rather than storing them in plain JSON.
- **Rate Limiting Expansion:** Broaden rate-limiting protections beyond authentication and inbox routes to encompass write-heavy automation surfaces.

## 3. Resume and Document System

- **Multi-Strategy Variants:** Introduce reusable, tailored resume variants organized by overarching role families rather than single jobs.
- **RenderCV Hardening:** Finalize live RenderCV production validation alongside strict artifact retention policies.
- **Preview Fidelity:** Enhance web previews so they visually align flawlessly with the final exported PDF artifacts.
- **Advanced Theming:** Integrate richer LaTeX or Typst-grade theme support while rigorously preserving ATS-safe defaults.

## 4. Discovery and Enrichment

- **Direct-Site Extraction:** Enhance direct-page extraction capabilities targeting complex company career sites and Workday-style portals.
- **Source Observability:** Implement comprehensive source-health diagnostics, retry visibility, and explicit stale-source alerting.
- **Coverage Expansion:** Broaden source coverage while strictly adhering to ATS-first deduplication and freshness semantics.
- **Retry Mechanisms:** Establish richer, automated per-source retry histories rather than relying solely on manual enrichment retries.

## 5. Company Intelligence

- **Data Deduplication:** Implement robust merge and duplicate-review workflows specifically for company records.
- **Portal Diagnostics:** Introduce portal-specific health checks and observability tooling.
- **Resolution Confidence:** Improve job-to-company resolution confidence scoring and provide a clearer override UX.

## 6. Automation Constraints

- **Field Adapter Breadth:** Expand generic field adapters to natively support file variants, address composites, and advanced site-specific controls.
- **Checkpoint Resumption:** Implement robust resume-from-last-checkpoint semantics for interrupted or partially completed application runs.
- **Site-Specific Adapters:** Broaden site-specific adapter coverage while guaranteeing safe, graceful fallback behaviors.

## 7. Inbox and OAuth Integrations

- **Live End-to-End Testing:** Finalize full live end-to-end verification of Gmail and Outlook OAuth integrations against actual provider credentials.
- **Token Management:** Implement robust token refresh telemetry, proactive re-auth prompts, and clear recovery UX for revoked credentials.
- **Provider Edge Cases:** Add specific provider tests verifying refresh-token rotation behaviors and invalid-grant handling.
- **Audit Tooling:** Integrate comprehensive connection audit histories and explicit revoke-access guidance within the diagnostics UI.

## 8. Diagnostics and Admin Tools

- **Operator Tooling:** Significantly expand the admin interface to better surface screenshot browsing, worker queue depths, and source-health drilldowns.
- **Search Capabilities:** Introduce advanced filtering and search tools across application run histories, feed events, and inbox OTP events.

## 9. Quality Assurance

- **Backend Integration Tests:** Add thorough integration test coverage spanning authentication, job ingestion, resume parsing, and file export pipelines.
- **Frontend E2E (Playwright):** Introduce Playwright E2E coverage specifically targeting sign-in, profile editing, job scoring, and resume parsing.
- **Automation E2E:** Build Playwright E2E coverage simulating inbox OAuth connections and OTP-assisted application pause states.
- **CI Pipelines:** Establish rigorous Continuous Integration for Python linting/testing alongside Web linting/building/typechecking.
