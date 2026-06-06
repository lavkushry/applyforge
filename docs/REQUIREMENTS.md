# ApplyForge Requirements

## System Purpose
ApplyForge operates as an advanced job hunt engine. It unifies resume extraction, continuous job discovery, targeted tailoring, and semi-automated application submission with strict safety guards.

## Non-Negotiable Boundaries
1. The master profile serves as the single source of truth for resume details.
2. The system **never** hallucinates qualifications or skills to increase application score.
3. The platform strictly enforces approval mechanisms for risky or unverified answers (e.g. salary, legal rights).
4. No CAPTCHA or anti-bot mechanism is forcefully bypassed; the platform will halt and request manual intervention.
5. All secrets, OTP codes, and user details must be aggressively masked in logging and output streams.

## Key Capabilities

### 1. Resume and Profile Parsing
- Supports ingestion of PDF, DOCX, and TXT files.
- Structures content into distinct metadata fields.
- Flags low-confidence extraction tasks for manual human review.

### 2. Output and Export Pipelines
- Offers several customizable, ATS-friendly light themes (Classic, Modern, Technical).
- Prioritizes plain-text extractability within PDFs.
- Provides a robust fallback renderer if the primary RenderCV template engine crashes.

### 3. Role Registry and Target Discovery
- Manages an ongoing target registry containing preferred salary, remote preferences, keywords, and blocked companies.
- Polls external APIs and specific ATS platforms (Greenhouse, Lever, etc) to find roles matching these targets.
- Merges duplicated job posts based on content heuristics and company URLs.

### 4. Smart Tailoring
- Generates precise gap analyses on missing job requirements.
- Emphasizes the candidate's existing strengths matching the description.
- Produces tailored cover letters mapped to the role constraints without violating truth guards.

### 5. Automated Apply Operations
- Automates simple browser flows via worker queues using Playwright.
- Captures granular UI states (screenshots) for each submission step.
- Supports "draft", "assisted", and "approved auto" application modes.

### 6. Email OTP Hooks
- Employs bounded OAuth grants for Gmail and Outlook to extract magic links or OTPs.
- Encrypts tokens heavily.
- Aborts gracefully if OTP retrieval fails within a specified time window, requiring manual input from the applicant.

## Quality Constraints
- UI latency should typically fall under 2 seconds for job feeds.
- Document tailoring needs to run under 10 seconds.
- OAuth logic demands scoped constraints to access only verification-level emails.