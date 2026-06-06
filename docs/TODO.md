# TODO / Remaining Hardening Work

## 1. Core Platform
- Deprecate startup `create_all` execution and adopt a full Alembic migration pipeline.
- Introduce S3 integration for remote object storage to replace local mounts.
- Wire up webhook/streaming interfaces for monitoring Celery tasks rather than strict polling.

## 2. Authorization & Security
- Overhaul basic cookie flow for a more robust refresh-token rotation setup.
- Enable granular route authorization rules (preparing for agency and multi-user scaling).
- Encrypt highly sensitive PII profile components.
- Enhance rate limits on aggressive write routes.

## 3. Resume Capabilities
- Fortify the RenderCV integration with reliable failure retention handling.
- Align web preview fidelity closer to the final PDF generation output.
- Add advanced LaTeX/Typst rendering engines without compromising ATS viability.

## 4. Discovery & Company Intel
- Develop broader job scraping schemas (specifically targeting Workday).
- Create automated company deduplication matching and merging UI.
- Expose deeper source-health metrics and failure alerts.
- Augment resolution matching when parsing generic jobs to companies.

## 5. Playwright Automation
- Multiply ATS field adapters to cover edge case navigation elements.
- Implement more resilient fallback mechanics for partially failed application checkpoints.

## 6. Inbox Hooks
- Build out full end-to-end integration test suites for Google and Outlook auth flows.
- Include explicit invalid-grant recoveries and revoke token alerts inside the diagnostics panel.

## 7. QA and Telemetry
- Enhance Playwright E2E coverage for sign-in, parsing, and scoring.
- Incorporate comprehensive E2E scopes for OTP parsing.
- Bolster the admin queue depth visualization panels.