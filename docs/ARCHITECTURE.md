# ApplyForge Architecture & Data Flow

This document details the high-level architecture, component boundaries, and primary data flows within the ApplyForge monorepo.

## System Components

ApplyForge is structured as a distributed system comprising three primary applications, supported by shared libraries.

### 1. `apps/web` (Frontend)
- **Framework**: Next.js (React) with TypeScript.
- **Responsibility**: Provides the interactive user interface, handling client-side routing, state management, and rendering data fetched from the API. It encompasses marketing pages, dashboards, job tracking boards, and configuration wizards.
- **Styling**: Tailwind CSS for utility-first styling.

### 2. `apps/api` (Backend API)
- **Framework**: FastAPI (Python).
- **Database ORM**: SQLAlchemy interacting with PostgreSQL.
- **Responsibility**: Serves as the core business logic engine. It manages authentication, handles CRUD operations for user profiles and jobs, executes the scoring and tailoring algorithms, and orchestrates the application run state machine.

### 3. `apps/worker` (Asynchronous Executor)
- **Framework**: Celery (Python) with Redis as the message broker.
- **Automation**: Playwright for browser interactions.
- **Responsibility**: Executes long-running and resource-intensive tasks offloaded by the API. This includes executing automated job applications, performing deep job enrichment scraping, and capturing diagnostic screenshots.

### 4. `packages/*` (Shared Infrastructure)
- **`packages/prompts`**: Centralized repository of LLM prompt templates used by the API for text generation and analysis.
- **`packages/config`**: Shared configuration schemas and discovery presets utilized by both the frontend wizard and backend ingestion services.

## Primary Data Flows

### The Ingestion Pipeline
1. **Trigger**: A job URL is submitted manually or discovered via an automated scrape.
2. **Normalization**: The API processes the raw job data, extracting key entities (Title, Company, Location, Requirements) and generating a deduplication key to prevent redundant entries.
3. **Enrichment (Async)**: If required, a task is queued to the Celery worker to fetch deeper context from the company's career portal using Playwright.
4. **Scoring**: The enriched job is evaluated against the user's canonical profile, resulting in a fit score and actionable recommendations.

### The Application Automation Flow
1. **Preparation**: The user initiates an application run. The API utilizes the LLM and the canonical profile to generate a tailored resume and draft a cover letter.
2. **Execution**: A task is dispatched to the Celery worker.
3. **Navigation**: The worker uses Playwright to navigate the application portal, utilizing predefined field mappings to populate forms.
4. **FSM Enforcement**: The execution follows a strict Finite State Machine. If an unknown or high-risk question is encountered, the worker pauses the run, captures a screenshot, and transitions the state to `paused`, awaiting user intervention via the web dashboard.
5. **Completion**: Upon successful submission (or manual approval), the run is marked `completed`, and relevant artifacts (tailored PDFs, final screenshots) are securely stored.

## Data Persistence Strategy

- **Relational Data**: PostgreSQL is the primary store for all structured data, including user accounts, profiles, job listings, application run states, and company directory entries.
- **Ephemeral State & Messaging**: Redis handles transient Celery task queues and serves as the backend for task results.
- **Artifact Storage**: Currently, generated PDFs and Playwright screenshots are persisted to the local file system. Transitioning to an S3-compatible object storage solution is a documented future requirement for scalable deployments.

## Security Boundaries

- The `apps/web` frontend communicates exclusively with the `apps/api` backend via RESTful endpoints over HTTP/HTTPS. It does not possess direct access to the PostgreSQL database or the Redis broker.
- The `apps/worker` interacts directly with the database to update task statuses and read required execution data, ensuring consistency without constantly polling the API.
