# TODO / Next Hardening Steps

This file tracks what still remains after the current resume-template, company-directory, preference-export, and FSM work.

## Platform

1. Remove runtime `create_all` and move fully to Alembic-managed migrations.
2. Add structured logging middleware and request IDs across API and worker.
3. Add S3-compatible storage adapter and signed downloads.
4. Add webhook or stream-based updates for long-running runs instead of polling only.

## Auth and security

1. Replace the basic cookie session flow with refresh-token rotation and stricter session policies.
2. Add per-route authorization layers for future multi-user and agency roles.
3. Encrypt sensitive profile answers at rest instead of leaving all preferences in plain JSON.
4. Add rate limiting and brute-force protection for auth and inbox-sensitive endpoints.

## Resume and document system

1. Replace JSON textareas in the profile editor with richer section-level editors.
2. Add multiple resume strategies and reusable tailored variants by role family.
3. Complete live RenderCV production validation and artifact retention rules.
4. Improve preview fidelity so web previews more closely match exported artifacts.
5. Add richer LaTeX or Typst-grade theme support while preserving ATS-safe defaults.

## Discovery and enrichment

1. Add richer direct-page extraction for company career sites and Workday-like pages.
2. Add source-health diagnostics, retry visibility, and stale-source alerts.
3. Expand source coverage while preserving ATS-first dedupe and freshness semantics.
4. Add operator-visible recovery for failed enrichment jobs.

## Company intelligence

1. Add company merge and review tooling for duplicate company records.
2. Add portal health checks and portal-level diagnostics.
3. Add better job-to-company resolution confidence tracking and override UX.

## Automation

1. Expand generic field adapters for selects, radios, checkboxes, date inputs, and multi-step flows.
2. Add richer resume-from-last-checkpoint semantics for partially completed runs.
3. Persist worker retry attempts and backoff metadata directly on run history.
4. Add stronger packet diagnostics and approval decision visibility.
5. Add broader site-specific adapters while keeping graceful fallback behavior.

## Inbox and OAuth

1. Complete live end-to-end Gmail and Outlook OAuth verification against real credentials.
2. Add token refresh telemetry, re-auth prompts, and revoked-credential recovery UX.
3. Add provider-specific tests for refresh-token rotation and invalid-grant handling.
4. Add connection audit history and revoke-access guidance in diagnostics.

## Diagnostics and admin

1. Expand the admin surface for worker queues, failed enrichment jobs, prompt traces, and screenshot browsing.
2. Add better filtering and search across run history, feed events, and OTP events.
3. Add retry controls directly from diagnostics for enrichment and apply runs.

## Quality

1. Add integration tests for auth, jobs, resume parsing, and file export.
2. Add Playwright E2E coverage for sign-in, profile edit, job scoring, and resume parsing.
3. Add Playwright E2E coverage for inbox OAuth connect and OTP-assisted application pauses.
4. Add CI for Python lint/tests and web lint/build/typecheck.
