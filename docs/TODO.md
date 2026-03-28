# TODO / Next Hardening Steps

This file tracks what remains after the current role-feed, themed-resume, and inbox-OAuth implementation.

## Platform

1. Remove runtime `create_all` and move fully to Alembic-managed migrations.
2. Introduce structured logging middleware and request IDs across API and worker.
3. Add S3-compatible storage adapter and signed downloads.
4. Add webhook or event-stream updates for long-running application runs.

## Security

1. Replace basic JWT cookie flow with refresh token rotation and stricter session policies.
2. Add per-route authorization layers for future multi-user and agency roles.
3. Encrypt sensitive profile answers at rest.
4. Add rate limiting and brute-force protection for auth endpoints.

## Resume and Documents

1. Replace JSON textareas with richer section-level profile editors.
2. Add multiple resume strategies and reusable tailored variants.
3. Complete live RenderCV/Typst production export validation with deterministic fallback policy and artifact retention rules.
4. Add richer preview fidelity so web previews match final exported layouts more closely.

## Jobs and Scoring

1. Add URL scraping workers for richer multi-source ingestion.
2. Add tunable weighting for location, visa, salary, and domain fit.
3. Expand source coverage while keeping ATS-first dedupe and freshness semantics intact.
4. Add source-health diagnostics, retry backoff visibility, and stale-source alerts.
5. Expand company resolution with review queues, merge tooling, and portal-health checks.

## Automation

1. Dispatch worker runs asynchronously from the API instead of inline skeleton logging.
2. Persist screenshots as uploaded file records directly from worker callbacks.
3. Expand generic field adapters for dropdowns, radios, file uploads, and multi-step ATS flows.
4. Add resume submission checkpoints and resume-failure recovery.
5. Add explicit automation eligibility rules per role and per job score threshold.
6. Add robust resume/restart semantics for partially completed application flows.

## Inbox and OAuth

1. Complete live end-to-end Gmail and Outlook OAuth verification against real developer credentials.
2. Add token refresh telemetry, re-auth prompts, and revoked-credential recovery UX.
3. Add provider-specific tests for refresh-token rotation and invalid-grant handling.
4. Add revoke-access guidance and connection audit history in diagnostics.

## Quality

1. Add integration tests for auth, jobs, resume parsing, and file export.
2. Add Playwright E2E tests for sign-in, profile edit, job scoring, and resume parsing.
3. Add Playwright E2E coverage for inbox OAuth connect and OTP-assisted application pauses.
4. Add CI for Python lint/tests and web typecheck/lint/build.
