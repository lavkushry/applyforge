# Upcoming Enhancements & Action Items

This document outlines the remaining engineering work following the completion of the resume-template, company-directory, preference-export, and finite-state machine (FSM) implementations.

## Infrastructure & Platform

1. Transition fully to Alembic-driven migrations, eliminating the use of runtime `create_all` database initializations.
2. Integrate an S3-compatible object storage provider, complete with securely signed download URLs.
3. Implement streaming or webhook-based progress updates for extended automation processes, replacing the current polling mechanism.

## Security & Authentication

1. Upgrade the current simple cookie session mechanism to a more robust model featuring refresh-token rotation and strict session lifecycle policies.
2. Introduce route-level authorization controls to lay the groundwork for multi-user and agency-level access roles.
3. Apply at-rest encryption for sensitive user profile responses rather than persisting preferences as plain JSON.
4. Broaden rate-limiting protections, extending them from just authentication and inbox endpoints to encompass all write-intensive automation routes.

## Documents & Resume Pipelines

1. Support diverse resume strategies and reusable tailored templates categorized by role family.
2. Finalize real-world RenderCV production testing and establish clear artifact retention policies.
3. Enhance the fidelity of the web-based resume preview so it accurately mirrors the final exported document.
4. Introduce more sophisticated LaTeX or Typst theme options while maintaining strict ATS compatibility as a baseline.

## Enrichment & Job Discovery

1. Develop advanced direct-page extraction capabilities for employer career portals, specifically targeting Workday and similar platforms.
2. Implement robust diagnostics for job sources, including retry transparency and notifications for stale or failing sources.
3. Increase the breadth of supported job sources without compromising ATS-centric deduplication and data freshness.
4. Deepen the historical retry logging for individual sources and configure active alerts for degraded data feeds, moving beyond mere manual retry triggers.

## Company Intelligence Framework

1. Build operator tools to review, merge, and deduplicate overlapping company profiles.
2. Establish health checks and diagnostic monitoring for company career portals.
3. Improve the confidence metrics and user-override interface for resolving jobs to specific company entities.

## Automation Engine

1. Extend the generic field adapter system to handle complex inputs such as file variants, multi-part addresses, and platform-specific UI controls.
2. Introduce comprehensive "resume-from-checkpoint" capabilities to handle and recover partially executed application runs.
3. Expand coverage with specialized, site-specific field adapters while ensuring fallback mechanisms remain intact.

## OAuth & Inbox Integrations

1. Perform comprehensive end-to-end testing for Gmail and Outlook OAuth flows using live provider credentials.
2. Implement detailed telemetry for token refresh cycles, proactive re-authentication prompts, and user flows for handling revoked credentials.
3. Create provider-specific automated tests to validate refresh-token rotation and gracefully handle invalid-grant scenarios.
4. Provide a clear audit trail for inbox connections and offer step-by-step guidance within the diagnostics UI for revoking access.

## Administration & Diagnostics

1. Enhance the admin dashboard to support deeper visibility into screenshot archives, queue backlogs, and detailed source-health metrics.
2. Implement advanced filtering and search functionalities across application run logs, job feed events, and OTP retrieval occurrences.

## Testing & Quality Assurance

1. Introduce comprehensive integration test suites covering authentication, job processing, resume parsing, and document generation.
2. Build end-to-end Playwright tests for core user journeys: sign-in, profile editing, job scoring, and resume ingestion.
3. Expand Playwright coverage to validate inbox OAuth connections and OTP-driven pauses during the application process.
4. Configure Continuous Integration (CI) pipelines to automatically execute Python formatting/testing and Next.js linting/building/typechecking.
