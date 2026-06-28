# ApplyForge TODO

This document tracks upcoming improvements, technical debt, and product features for ApplyForge.

## High Priority

- Expand worker test coverage for edge cases during Playwright interactions.
- Implement robust retry mechanisms with exponential backoff for Celery tasks.
- Finalize schema migrations and enable Alembic in production.
- Refine error handling in the FastAPI layer to ensure user-friendly error messages.

## Medium Priority

- Enhance the web dashboard with more detailed analytics on job application statuses.
- Support cloud-based file storage (e.g., AWS S3, Google Cloud Storage) instead of local disk storage.
- Implement comprehensive e2e tests for the Next.js frontend using Playwright.
- Improve accessibility (a11y) across the web application, following ARIA best practices.
- Add support for multiple resume templates (e.g., visual templates, non-ATS templates).

## Low Priority

- Explore integrating advanced LLM capabilities for cover letter generation.
- Implement multi-tenant support for agency or team-based workflows.
- Investigate caching strategies (e.g., Redis caching for API responses) to improve performance.

## Completed

- Setup FastAPI backend and Next.js frontend scaffolding.
- Implement basic resume parsing and job scoring capabilities.
- Integrate initial Celery worker for background processing.
- Build the manual job ingestion and role discovery flows.
