# ApplyForge TODO & Hardening Roadmap

This document outlines the remaining hardening steps and critical pending tasks following the recent implementations of the resume-template engine, company-directory foundation, preference-export, and run-state machine (FSM).

---

## 🏗️ Platform & Infrastructure

1. **Strict Migrations:** Remove the runtime `Base.metadata.create_all(...)` entirely and transition the system fully to Alembic-managed database migrations.
2. **Durable Storage:** Implement an S3-compatible storage adapter to handle uploaded files and run artifacts, replacing local disk storage. Include support for securely signed download URLs.
3. **Real-time Updates:** Transition long-running application runs from client-side polling to a webhook or Server-Sent Events (SSE) stream-based update model.

---

## 🔐 Authentication & Security

1. **Session Hardening:** Replace the basic cookie session implementation with a robust refresh-token rotation architecture and stricter session expiration policies.
2. **Authorization Layers:** Implement granular, per-route authorization controls to support future multi-user enterprise and agency role environments.
3. **Data Encryption:** Encrypt sensitive profile answers at rest rather than storing all user preferences as plaintext JSON blobs.
4. **Rate Limiting:** Expand strict rate limiting beyond authentication and inbox-sensitive endpoints to encompass broader write-heavy automation API surfaces.

---

## 📄 Resume & Document System

1. **Multi-Strategy Support:** Implement robust support for multiple overarching resume strategies, allowing users to maintain reusable tailored variants segregated by distinct role families.
2. **RenderCV Hardening:** Complete the live RenderCV production validation phase and define strict artifact retention and cleanup rules.
3. **Preview Fidelity:** Enhance the web preview engine so that live UI previews perfectly match the final exported PDF artifacts.
4. **Advanced Formatting:** Introduce richer LaTeX or Typst-grade theme support while rigorously preserving ATS-safe default outputs.

---

## 🔍 Discovery & Job Enrichment

1. **Deep Extraction:** Build richer direct-page extraction capabilities specifically tailored for complex company career sites and multi-page Workday-like portals.
2. **Source Health Monitoring:** Implement comprehensive source-health diagnostics, granular retry visibility, and automated stale-source alerting for operators.
3. **Coverage Expansion:** Expand overall source coverage breadth while strictly maintaining the system's ATS-first deduplication and freshness event semantics.
4. **Retry Tooling:** Build out a richer per-source retry history interface in the operator dashboard, moving beyond basic manual enrichment retry triggers.

---

## 🏢 Company Intelligence

1. **Deduplication Tooling:** Build comprehensive company merge and duplicate-review tooling for administrators managing the company graph.
2. **Portal Diagnostics:** Implement automated portal health checks and expose portal-level diagnostics in the internal admin UI.
3. **Resolution Confidence:** Improve job-to-company resolution heuristics, add explicit confidence scoring, and provide a clear UI for manual resolution overrides.

---

## 🤖 Automation Execution

1. **Advanced Field Adapters:** Expand generic Playwright field adapters to seamlessly handle complex file variants, composite address inputs, and increasingly esoteric, site-specific UI controls.
2. **Resumption Semantics:** Build robust resume-from-last-checkpoint capabilities for application runs that experience partial or intermittent failures.
3. **Site-Specific Adapters:** Develop a broader array of site-specific navigation adapters while ensuring the system retains its graceful fallback pause behavior.

---

## 📧 Inbox & OAuth Integrations

1. **End-to-End Verification:** Complete live, end-to-end verification of Gmail and Outlook OAuth flows against production-grade provider credentials.
2. **Recovery UX:** Implement comprehensive token refresh telemetry, proactive re-auth prompts, and clear UX recovery paths for revoked credentials.
3. **Provider Testing:** Add strict provider-specific automated tests to handle refresh-token rotation failures and invalid-grant exceptions.
4. **Audit History:** Display comprehensive connection audit histories and explicit revoke-access guidance directly within the user diagnostics panel.

---

## 🛠️ Diagnostics & Administration

1. **Artifact Browsing:** Expand the admin surface to allow deep inspection of screenshot sequences, run queue depths, and source-health drilldowns.
2. **Global Search:** Implement robust global filtering and search capabilities across run histories, feed events, and OTP retrieval events.

---

## ✅ Quality Assurance

1. **Integration Coverage:** Expand integration test coverage targeting authentication flows, job scoring algorithms, resume parsing engines, and file export pipelines.
2. **E2E Playwright Coverage (Web):** Add comprehensive E2E tests for the sign-in flow, profile editing, job scoring interfaces, and resume parsing UI.
3. **E2E Automation Coverage:** Implement targeted Playwright E2E coverage verifying the inbox OAuth connection flows and OTP-assisted application pause gates.
4. **CI/CD Pipelines:** Implement rigorous CI pipelines enforcing Python lint/tests (`make api-test`) and web lint/build/typecheck (`make web-typecheck`) on all PRs.