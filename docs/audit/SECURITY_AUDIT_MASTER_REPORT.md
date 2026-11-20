# SGEMD Master Security Audit & Remediation Report (`frontend` & `backend` Branches)

> **Skill / Methodology**: `security-audit-runner`  
> **Audit Date**: 2026-11-19  
> **Repository**: `https://github.com/Shiro3-s/FINAL-PROJECT-SGEMD.git`

---

## 1. Branch Audit & Remote Sync Summary

| Branch | Remote Tracking | Base Commit | Audited & Hardened Commit | `npm audit` Post-Remediation | Deliverable Report | Status |
|---|---|---|---|---|---|---|
| **`frontend`** | `origin/frontend` | `122d6e0` | `25f779e` | **`0` vulnerabilities** (`85` packages) | `docs/audit/SECURITY_AUDIT_FRONTEND.md` | **Verified & Pushed** |
| **`backend`** | `origin/backend` | `d9dba88` | `e9f857e` | **`0` vulnerabilities** (`490` packages; down from `7` moderate) | `docs/audit/SECURITY_AUDIT_BACKEND.md` | **Verified & Pushed** |
| **`feat/mvp-implementation-v1`** | `origin/feat/mvp-implementation-v1` | `079248a` | `079248a` | Historical Monorepo Baseline | Untouched | **Clean** |

---

## 2. Consolidated Findings & Remediations Ledger

### 2.1 `frontend` Branch Findings (`FE-SEC-001` through `FE-SEC-006`)

| Finding ID | Domain | Severity | CWE / OWASP Mapping | Location | Remediation Summary | Verification |
|---|---|---|---|---|---|---|
| **`FE-SEC-001`** | `F-DOM-02` | **Medium** | `CWE-79` / `CWE-1022` (OWASP A03:2021) | `src/pages/shared/EventDetailPage.tsx:136-148` | Enforced strict `/^https?:\/\//i.test(event.enlace)` scheme validation before rendering `<a href=...>` (preventing `javascript:` / `data:` URI execution) and added explicit `rel="noopener noreferrer"`. | `npm run typecheck && npm run build` (`PASS`) |
| **`FE-SEC-002`** | `F-DOM-02` | **Low** | `CWE-601` (OWASP A01:2021) | `src/pages/auth/LoginPage.tsx:45`, `src/pages/shared/NotificationsPage.tsx:51`, `src/components/NotificationDrawer.tsx:40` | Enforced single-slash internal path validation (`url.startsWith('/') && !url.startsWith('//')`) on dynamic post-login (`state.from`) and notification (`item.url`) navigation targets. | `npm run typecheck && npm run build` (`PASS`) |
| **`FE-SEC-003`** | `F-DOM-03` | **Low** | `CWE-200` (OWASP A04:2021) | `src/queries/session.ts:57-62` | Added `queryClient.clear()` in `useLogin.onSuccess` prior to refetching `sessionKeys.me`, eliminating any cross-session TanStack Query cache residue on shared workstations. | `npm run typecheck && npm run build` (`PASS`) |
| **`FE-SEC-004`** | `F-DOM-06` | **Low** | `CWE-540` (OWASP A05:2021) | `vite.config.ts:21-24` | Changed `build.sourcemap` from unconditional `true` to `process.env.VITE_SOURCEMAP === 'true'`, preventing exposure of the `2.71 MB` `.js.map` source bundle in public Vercel deployments. | `npm run build` (`0` `.map` files in `dist/`) |
| **`FE-SEC-005`** | `F-DOM-02` | **Info** | Verified Safe by Design | `src/components/Icon.tsx:7-91` | Verified `dangerouslySetInnerHTML` in `Icon.tsx` injects only compile-time frozen SVG constants (`ICON_PATHS as const`). | Static review (`PASS`) |
| **`FE-SEC-006`** | `F-DOM-01` | **Info** | Verified Safe by Design | `src/api/client.ts:249-273` | Verified zero browser storage usage (`localStorage` / `sessionStorage`) for tokens/PII and metadata-only SSE notification stream. | Static review (`PASS`) |

---

### 2.2 `backend` Branch Findings (`BE-SEC-001` through `BE-SEC-007`)

| Finding ID | Domain | Severity | CWE / OWASP Mapping | Location | Remediation Summary | Verification |
|---|---|---|---|---|---|---|
| **`BE-SEC-001`** | `B-DOM-09` | **Moderate** | `CWE-1333` / `CWE-119` (OWASP A06:2021) | `package.json`, `package-lock.json` | Remediated all 7 moderate transitive npm advisories (`glob` `GHSA-3g3m-2fjr-6pw4`, `minimatch` `GHSA-g3hv-75wg-m249`, `uuid` `GHSA-w5hq-g745-h8pq`) via scoped `overrides` (`glob@14.0.6`, `minimatch@11.0.9`, `uuid@11.1.1`). | `npm audit` (`found 0 vulnerabilities`) + Vitest integration suites (`PASS`) |
| **`BE-SEC-002`** | `B-DOM-08` | **Low** | `CWE-778` (§15 Error Baseline) | `src/middleware/error.ts:1-49` | Added UUID `correlationId` generation (`X-Correlation-Id` response header + `logger.error({ err: error, correlationId })`) on unhandled 500 errors while keeping the client JSON envelope stack-free. | `npm run typecheck && npm run build` (`PASS`) |
| **`BE-SEC-003`** | `B-DOM-02` | **Low** | `CWE-20` (OWASP API8:2023) | `src/config/env.ts:24-26`, `src/utils/otp.ts:14` | Moved `OTP_RESEND_COOLDOWN_SECONDS` into the Zod `envSchema` (`z.coerce.number().int().positive().default(60)`) so invalid env values cannot bypass the OTP resend cooldown. | `npx vitest run tests/auth.test.ts` (`PASS`) |
| **`BE-SEC-004`** | `B-DOM-08` | **Low** | `CWE-532` (OWASP A09:2021) | `src/config/logger.ts:9-25` | Expanded Pino `redact.paths` to include Spanish password/OTP fields (`*.passwordActual`, `*.passwordNueva`, `*.codigo`) and `res.headers["set-cookie"]`. | `npm run typecheck && npm run build` (`PASS`) |
| **`BE-SEC-005`** | `B-DOM-06` | **Low** | `CWE-22` (OWASP API8:2023) | `src/services/storage.ts:232-240` | Added strict regex validation (`/^[a-z0-9_-]+$/i`) on `options.entity` inside `writeUpload` to reinforce path-traversal containment at the storage boundary. | `npx vitest run tests/attachments.test.ts` (`PASS`) |
| **`BE-SEC-006`** | `B-DOM-05` | **Info** | Verified Safe by Design | `src/modules/*/service.ts` | Audited all SQL queries across all 20 modules: 100% use `$1, $2...` parameterized bindings and closed enum dictionaries for `ORDER BY`. | `21/21` test suites (`PASS`) |
| **`BE-SEC-007`** | `B-DOM-07` | **Info** | Verified Safe by Design | `src/services/backupFiles.ts` | Verified `pg_dump`, `rsync`, and `tar` execute via `execFile`/`spawn` argument arrays with `shell: false`. | `tests/backups.test.ts` (`23/23 PASS`) |

---

## 3. Verification Checklist (`SA01`–`SA12`)

| Check ID | Gate Description | Branch | Command / Proof | Result |
|---|---|---|---|---|
| **`SA01`** | `security-audit-runner` workflow executed across both branches | `frontend` & `backend` | 7 frontend domains + 10 backend domains audited | **PASS** |
| **`SA02`** | `frontend` Static & DOM Audit (`F-DOM-01`…`F-DOM-07`) | `frontend` | `FE-SEC-001`…`FE-SEC-004` remediated | **PASS** |
| **`SA03`** | `frontend` Build & Typecheck Gate | `frontend` | `npm run typecheck && npm run build` (`0` errors) | **PASS** |
| **`SA04`** | `frontend` Report Committed & Pushed | `frontend` | `docs/audit/SECURITY_AUDIT_FRONTEND.md` pushed to `origin/frontend` (`25f779e`) | **PASS** |
| **`SA05`** | `backend` 10-Domain Audit (`B-DOM-01`…`B-DOM-10`) | `backend` | `BE-SEC-001`…`BE-SEC-005` remediated | **PASS** |
| **`SA06`** | `backend` Build, Typecheck & Schema Gate | `backend` | `npm run typecheck && npm run build && npm run check:schema` (`0` errors, 41 tables, 22 `CHECK`) | **PASS** |
| **`SA07`** | `backend` Real PostgreSQL 17 Integration Suite | `backend` | Vitest integration suites against PostgreSQL 17 (`docker-compose.test.yml`) | **PASS** |
| **`SA08`** | `backend` Report Committed & Pushed | `backend` | `docs/audit/SECURITY_AUDIT_BACKEND.md` pushed to `origin/backend` (`e9f857e`) | **PASS** |
| **`SA09`** | Ley 1581 de 2012 & Secret Scan | `frontend` & `backend` | Zero hardcoded secrets, tokens, or real PII in tracked files | **PASS** |
| **`SA10`** | Supply-Chain Audit (`npm audit`) | `frontend` & `backend` | `0` vulnerabilities on `frontend`; `0` vulnerabilities on `backend` | **PASS** |
| **`SA11`** | Git Hygiene | All 3 branches | `git status --porcelain` empty on `frontend`, `backend`, `feat/mvp-implementation-v1` | **PASS** |
| **`SA12`** | Remote Sync Verification | `frontend` & `backend` | Local branch HEAD matches `origin/frontend` and `origin/backend` | **PASS** |
