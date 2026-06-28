# ApplyForge Core Requirements

This document outlines the fundamental functional and non-functional requirements governing the ApplyForge system architecture and product development.

## 1. Core Platform Requirements

### 1.1 Centralized Profile Management
- The system must support comprehensive CRUD (Create, Read, Update, Delete) operations for a user's canonical professional profile.
- The canonical profile must serve as the absolute source of truth for all downstream document generation and application data entry.
- Users must be able to upload existing resumes, which the system will intelligently parse to populate the canonical profile.

### 1.2 Job Discovery & Ingestion
- The system must provide mechanisms for manual job ingestion.
- The system must support automated, role-based job discovery (scraping) from configured external sources.
- Ingested jobs must undergo a normalization process to standardize titles, companies, and requirements.
- The system must prevent duplicate job entries using robust deduplication keys.

### 1.3 Intelligent Job Scoring
- Every ingested job must be scored against the user's canonical profile and targeted role preferences.
- The scoring mechanism must be transparent, providing users with clear, understandable reasons for the assigned score.
- The system must highlight missing skills and provide actionable recommendations for improving fit.

### 1.4 Generative Document Tailoring
- The system must dynamically generate tailored resumes and cover letters optimized for specific job requirements.
- **Strict Invariant**: The generative system is strictly forbidden from fabricating facts or experiences. It may only optimize the phrasing and presentation of existing data from the canonical profile.
- Generated documents must be exportable in ATS-friendly PDF formats.

### 1.5 Automated Application Execution
- The system must utilize a background worker (e.g., Celery + Playwright) to navigate and interact with external job application portals.
- Application execution must support distinct modes: "assisted" (requiring user checkpoints) and "auto-run" (fully automated where possible).
- The execution engine must maintain a durable, inspectable log of every step taken during an application run.

## 2. Security & Compliance Requirements

### 2.1 Authentication & Authorization
- User authentication must be implemented using secure, HTTP-only cookies to mitigate XSS attacks.
- Access to all sensitive API endpoints must require valid session validation.

### 2.2 Data Privacy & Masking
- The system must never expose sensitive user data (e.g., passwords, raw OAuth tokens) in application logs or UI responses.
- Responses to high-risk application questions (e.g., salary expectations, visa status, demographic information) must require explicit, manual user approval before submission by the automation engine.

### 2.3 Integration Security
- OAuth integrations (e.g., for Gmail or Outlook OTP retrieval) must strictly adhere to the principle of least privilege, requesting only the scopes necessary for read-only email access.

## 3. Operational & Reliability Requirements

### 3.1 Background Task Processing
- Long-running tasks, such as job enrichment and browser automation, must be offloaded to a resilient message queue (e.g., Redis/Celery).
- The worker system must implement robust retry policies with exponential backoff for transient failures.

### 3.2 State Management
- Application automation runs must be governed by a strict Finite State Machine (FSM), ensuring predictable transitions between states (`queued`, `running`, `paused`, `failed`, `completed`, etc.).
- The system must gracefully handle interruptions; if a worker fails, the application run state must accurately reflect the failure and permit resumption or manual intervention.

### 3.3 Observability
- The system must generate real-time feed events for significant state changes (e.g., new jobs ingested, score updates, application failures).
- Operators must have access to diagnostic views detailing the timeline and granular step logs of automation runs.

## 4. Development & Maintenance Guidelines

### 4.1 Monorepo Structure
- The codebase must be maintained as a monorepo, enforcing clear boundaries between the frontend (`apps/web`), backend API (`apps/api`), worker (`apps/worker`), and shared packages (`packages/*`).

### 4.2 Quality Assurance
- All critical business logic, specifically within the scoring, tailoring, and FSM modules, must be backed by comprehensive unit tests.
- Code modifications must pass automated linting, type-checking (TypeScript), and static analysis checks prior to deployment.
