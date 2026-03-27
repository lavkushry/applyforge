# TODO / Next Hardening Steps

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
3. Upgrade PDF rendering to a more polished typographic engine.

## Jobs and Scoring

1. Add URL scraping workers for richer multi-source ingestion.
2. Persist latest score snapshots on jobs for faster dashboard access.
3. Add tunable weighting for location, visa, salary, and domain fit.

## Automation

1. Dispatch worker runs asynchronously from the API instead of inline skeleton logging.
2. Persist screenshots as uploaded file records directly from worker callbacks.
3. Expand generic field adapters for dropdowns, radios, file uploads, and multi-step ATS flows.
4. Add resume submission checkpoints and resume-failure recovery.

## Quality

1. Add integration tests for auth, jobs, resume parsing, and file export.
2. Add Playwright E2E tests for sign-in, profile edit, job scoring, and resume parsing.
3. Add CI for Python lint/tests and web typecheck/lint.
