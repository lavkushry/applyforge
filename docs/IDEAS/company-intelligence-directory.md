# Idea: Company Intelligence Directory

This document outlines the conceptual foundation and planned implementation for the Company Intelligence Directory within ApplyForge.

## Concept Overview

Currently, ApplyForge treats "Companies" primarily as string attributes attached to "Jobs". The Company Intelligence Directory aims to elevate companies to first-class entities within the system. This directory will serve as a centralized knowledge base for specific employers, enriching the application process with deeper context.

## Core Capabilities

1. **Centralized Information Hub**: Store aggregated data about a company, including industry, size, mission statement, and core values.
2. **Application Portal Mapping**: Maintain verified links to the company's primary career portal and specific ATS instances (e.g., distinguishing between a company's Workday instance and their corporate site).
3. **Contact Registry**: Track known recruiter contacts or hiring managers associated with the company, facilitating targeted follow-ups.
4. **Historical Interaction Tracking**: Provide a unified view of all past job applications, interviews, and outcomes associated with a specific company across the user's history.

## Technical Implementation Plan

### Database Schema Evolution
- Create a dedicated `Company` model in SQLAlchemy.
- Establish foreign key relationships linking the `Job` model to the new `Company` model.
- Implement models for `CompanyPortal` and `CompanyContact` linked back to the primary `Company` entity.

### API Enhancements
- Develop dedicated CRUD endpoints (`/api/companies/*`) to manage company records.
- Update the job ingestion pipeline to attempt automatic resolution and linking to existing company records based on normalized names or domains.

### UI Integration
- Build a `/companies` dashboard in the Next.js frontend, providing a searchable directory view.
- Enhance the job detail view to include a "Company Snapshot" sidebar, surfacing relevant intelligence during the application review phase.

## Potential Future Expansions

- **Automated Intelligence Gathering**: Utilize the Celery worker to periodically scrape company "About Us" pages to automatically refresh mission statements and values.
- **Network Graphing**: Visually map connections between companies (e.g., parent/subsidiary relationships) or identify potential internal referral networks based on the user's uploaded contact list.
