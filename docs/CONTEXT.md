# ApplyForge Context Overview

## Core Concept
ApplyForge is a comprehensive operating system designed to optimize the job-hunting process. It breaks down into five continuous phases:
1. Intelligent resume and profile parsing.
2. Targeted role discovery and job enrichment.
3. Automated and transparent application scoring and tailoring.
4. Browser-assisted, secure job application execution.
5. In-depth diagnostics, OTP extraction, and manual operator reviews.

## Platform Features
The platform is fully functional with:
- Cookie-based authentication mechanisms.
- CRUD operations for user profiles.
- Automated resume extraction.
- Various ATS-friendly resume themes.
- RenderCV fallbacks.
- Intelligent discovery run feeds that capture near real-time role tracking.
- Contact tracking, company discovery, and job portals routing.
- Worker queues dedicated to scraping and application submission via Playwright.
- End-to-end FSM state tracking.
- Gmail and Outlook OAuth integrations for automated OTP handling.

## Guiding Principles
- **Immutable Profiles**: Profiles remain the final source of truth; never fabricate user data.
- **Role-Driven Scopes**: A user's specified role governs the application automation logic.
- **Presentation is Ephemeral**: Resumes and templates are strictly for presentation; they do not dictate the user profile data model.
- **Fail Gracefully**: Partially executed applications must pause and remain available for operator review.
- **Security First**: All access tokens, OTPs, and sensitive user secrets are heavily masked and guarded by authorization logic.

## Essential Codebase References
**Resume & Export Logic:**
- `apps/api/app/services/resume_parser.py`
- `apps/api/app/services/resume_themes.py`
- `apps/api/app/services/resume_templates.py`

**Job Intelligence & Scoring:**
- `apps/api/app/services/role_ingestion.py`
- `apps/api/app/services/job_dispatch.py`
- `apps/api/app/services/job_enrichment.py`
- `apps/api/app/services/scoring.py`

**Automation & Packets:**
- `apps/api/app/services/application_packets.py`
- `apps/worker/app/playwright_runner.py`
- `apps/api/app/services/application_fsm.py`

## Validation Guidelines
To verify new changes to the environment:
1. `make lint`
2. `make web-typecheck`
3. `make api-test`

*Note: Application execution paths and field coverage mapping are continually evolving but active.*