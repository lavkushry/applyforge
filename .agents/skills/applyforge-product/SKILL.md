---
name: applyforge-product
description: Product and domain guidance for ApplyForge. Use when building resume intelligence, job scoring, tailoring, and application workflow features.
---

# ApplyForge Product Skill

## Product invariants

- The canonical candidate profile is the only trusted source of resume facts.
- Tailoring may reorder or emphasize facts, but never invent them.
- Job scores must explain tradeoffs, not just output a number.
- Application automation must pause for risky prompts and unknown answers.

## Preferred implementation patterns

- Keep feature boundaries explicit: profile, jobs, tailoring, applications, diagnostics.
- Persist operational evidence for every automation run.
- Prefer transparent heuristics over opaque AI calls when building the MVP.

## UI expectations

- Make the dashboard feel like a real operating system, not a list of forms.
- Surface recommendation, status, and next-step context in every workflow.
