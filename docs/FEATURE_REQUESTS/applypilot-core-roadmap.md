# ApplyForge Roadmap: ApplyPilot Core Parity

This document tracks the progress toward achieving feature parity with the conceptual ApplyPilot product roadmap.

## Objective

The goal is to evolve ApplyForge into a comprehensive, end-to-end job search automation platform that significantly reduces the friction of discovering, tracking, and applying for relevant roles.

## Phase 1: Foundation & Discovery (Completed)

- [x] Basic user authentication and session management.
- [x] Canonical profile creation and resume parsing integration.
- [x] Manual job URL ingestion and basic data normalization.
- [x] Implementation of the core job scoring algorithm based on profile fit.
- [x] Development of the fundamental web dashboard and job tracking list.
- [x] Role-based discovery presets for targeted job searching.

## Phase 2: Document Intelligence (Completed)

- [x] Dynamic resume tailoring prioritizing existing facts over hallucination.
- [x] Integration of PDF generation tools for ATS-compliant resume exports.
- [x] Support for Markdown and LaTeX resume starter templates.
- [x] Basic cover letter generation aligned with specific job descriptions.
- [x] Centralized application tracking board within the web interface.

## Phase 3: Automation Execution (In Progress)

- [x] Implementation of the Finite State Machine (FSM) for application runs.
- [x] Integration of the Celery/Playwright worker for browser automation.
- [x] Support for "assisted" application modes requiring manual review checkpoints.
- [x] Capture and storage of diagnostic screenshots during automation failures.
- [ ] Expansion of automated field mapping to support a wider array of ATS platforms (e.g., Workday, Greenhouse, Lever).
- [ ] Full implementation of "auto-run" mode for highly confident application submissions.
- [ ] Comprehensive handling of complex form inputs (e.g., dynamic dropdowns, multi-page forms).

## Phase 4: Enterprise & Scale (Planned)

- [ ] Migration from local disk storage to S3-compatible object storage for all artifacts.
- [ ] Implementation of full database schema migrations using Alembic for production stability.
- [ ] Multi-tenant support to enable agency workflows and team-based collaborations.
- [ ] Advanced analytics dashboard detailing application success rates and pipeline bottlenecks.
- [ ] Browser extension for one-click job ingestion directly from external job boards.
