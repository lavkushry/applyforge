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

## Observability rules

- Prompt metadata should be logged with masked sensitive values.
- Admin diagnostics should expose run state, failures, and prompt traces.
- Worker code should return structured artifacts, not plain strings.
