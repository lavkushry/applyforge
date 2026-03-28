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
- Resume themes are presentation-layer choices, not new sources of truth.
- Role strategy is the primary control plane for job discovery and automation eligibility.

## Preferred implementation patterns

- Keep feature boundaries explicit: profile, jobs, tailoring, applications, diagnostics.
- Persist operational evidence for every automation run.
- Prefer transparent heuristics over opaque AI calls when building the MVP.
- Treat score explanations, missing skills, and recommendation text as user-facing product surfaces.
- Keep ATS-safe output paths available even when richer renderers or providers fail.

## Current domain map

- `profile`: canonical user facts, saved answers, preferences
- `roles`: target role strategy, cadence, thresholds, source subscriptions
- `jobs`: normalized job record, feed events, score history
- `documents`: tailored resume versions, themes, cover letters, export state
- `applications`: run status, step evidence, approval gates, OTP assistance
- `diagnostics`: scrape failures, prompt traces, OTP events, worker evidence

## Product decisions already made

- The MVP is ATS-first, single-column-first, and truth-constrained.
- Near-realtime means feed polling and durable event history, not guaranteed socket streaming.
- Supported inbox providers are Gmail and Outlook only.
- OTP access is narrowly scoped to help complete the user’s own application flow.
- RenderCV compatibility is desirable, but export continuity matters more than renderer purity.

## UI expectations

- Make the dashboard feel like a real operating system, not a list of forms.
- Surface recommendation, status, and next-step context in every workflow.
- Show operator readiness where integrations need setup, instead of failing silently.
- Keep diagnostics legible to both product builders and power users reviewing automation behavior.
