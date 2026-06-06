# Company Intelligence Matrix

## Overview
What began as an idea has successfully morphed into core infrastructure. ApplyForge now manages user-scoped company entities, mapping external jobs directly to tracked companies.

## What's Live Now
- The schema houses `companies`, `company_career_portals`, and `company_contacts`.
- Standard API endpoints cover CRUD operations for these models.
- The web UI integrates company listings, selection modalities, and link visibility.
- Manual application generation hooks automatically match jobs against known internal entities.

## Target Expansion Priorities
To further refine the company matrix, the following are needed:
1. Merge and duplicate remediation utilities for operators to clean up the directory.
2. Portal-specific health polling to ensure career sites haven't altered their DOM structure.
3. Expanded confidence scoring rules when predicting company associations.
4. Robust recruitment metadata scraping.

## The Strategy Going Forward
This intelligence directory must serve as a central pillar to reduce duplicate discovery loads and to track overarching automation policies defined per company rather than per job. Future updates should solely expand this existing graph.