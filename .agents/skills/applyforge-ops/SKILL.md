---
name: applyforge-ops
description: Operational guidance for ApplyForge automation, prompt logging, diagnostics, and worker flows.
---

# ApplyForge Ops Skill

## Automation rules

- Every run should have durable step logs.
- Screenshots should be captured at meaningful transitions.
- Unknown answers must become review gates, not silent defaults.
- Retriable failures should preserve context for resume/restart behavior.
- OTP lookup should be logged as its own step kind with masked outputs.
- Integration setup failures should surface as readiness state, not opaque runtime crashes.

## Observability rules

- Prompt metadata should be logged with masked sensitive values.
- Admin diagnostics should expose run state, failures, and prompt traces.
- Worker code should return structured artifacts, not plain strings.
- OAuth and inbox responses must never expose stored encrypted token material.

## Current operational hotspots

- `role_ingestion.py`: source fetch failures, dedupe drift, freshness updates
- `files.py`: renderer fallback behavior and artifact retention
- `inbox.py`: provider setup, token refresh, OTP extraction confidence
- `applications.py`: pause gates, submit uncertainty, resume/restart state

## Verification expectations

- Backend changes should keep `pytest` green for route and service coverage.
- Web settings or integration UX changes should be verified with `lint`, `build`, and then `typecheck`.
- If a repo command depends on `.next/types`, prefer running `build` before `typecheck`.
