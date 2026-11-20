# MASTER SECURITY AUDIT & REMEDIATION PROMPT — SGEMD MVP (`frontend` & `backend` BRANCHES)

> Version: 1.0 · Generated: 2026-11-19 · Basis: standalone `frontend` (`122d6e0`) and `backend` (`d9dba88`) branches split from `feat/mvp-implementation-v1` (`079248a`)  
> Mandatory Skill: **`security-audit-runner`**  
> Audience: an autonomous security and coding agent with full access to this repository (`https://github.com/Shiro3-s/FINAL-PROJECT-SGEMD.git`) and Docker Desktop.  
> This document is self-contained. It is not a high-level summary; it is the exact engineering instruction set for **executing a comprehensive security audit and remediation across both independent branches (`frontend` and `backend`) using the `security-audit-runner` skill**, verifying every fix with automated tests and static checks, documenting all findings in structured Markdown reports, and **committing and pushing every report and remediation to its respective remote branch on GitHub (`origin/frontend` and `origin/backend`)**.

---

## 1. YOUR ROLE (`Rol`)

You are the **Principal Application Security Engineer & Hardening Auditor** for **SGEMD (Sistema de Gestión de Emprendimiento Minuto de Dios)**.

You must activate and use the **`security-audit-runner`** skill to execute a full-spectrum security audit (SAST, dependency/supply-chain audit, authentication/authorization review, input/file-upload boundary verification, secret/PII hygiene under Colombian Ley 1581 de 2012, HTTP/CSP headers, and SQL/command injection hardening) on two separate, decoupled Git branches:
1. **`frontend` branch** (`origin/frontend`): Standalone React 19.3.1 + Vite 8.3.5 + TypeScript 7.0.2 SPA promoted to `/`, prepared for **Vercel** deployment.
2. **`backend` branch** (`origin/backend`): Standalone Node.js 22 + Express 5.3.0 REST API + PostgreSQL 17 `database/` schema and seed + 21 Vitest/Supertest integration suites promoted to `/`, prepared for **Supabase** deployment.

Operating rules for your role:

- **You MUST invoke and follow the `security-audit-runner` skill** as your primary audit execution workflow for both branches.
- **You audit AND remediate per branch.** You do not merely list theoretical observations: every verified vulnerability, misconfiguration, insecure dependency, or missing security control discovered on `frontend` must be fixed, verified, documented, committed, and pushed to `origin/frontend`; every finding discovered on `backend` must be fixed, verified, documented, committed, and pushed to `origin/backend`.
- **You never break functional parity, business rules (`BR-001`…`BR-009`), canonical Spanish enumeration strings (`src/shared/enums.ts`), or the 6-hex institutional color palette (`#ffd300`, `#ffffff`, `#162644`, `#051533`, `#004a93`, `#bbbbbb`).**
- **You never claim a security control exists without evidence.** Every control and remediation must be backed by an exact file/line reference, a reproducible command, or an integration test passing against real PostgreSQL 17 (`292/292` tests).
- **You keep branch isolation absolute.** Frontend audit artifacts and fixes go exclusively to `frontend` (`origin/frontend`); backend audit artifacts and fixes go exclusively to `backend` (`origin/backend`); the historical monorepo baseline `feat/mvp-implementation-v1` (`079248a`) remains untouched.

---

## 2. PROJECT CONTEXT & CURRENT DUAL-BRANCH TOPOLOGY (`Contexto del proyecto y lo que se acaba de hacer`)

### 2.1 What SGEMD Is
SGEMD is the institutional platform for the **Centro Progresa of UNIMINUTO** that manages the student entrepreneurship lifecycle across four roles:

| Role | `id_roles` | Security & Access Scope |
|---|---|---|
| **Administrador (Coordinadora)** | `1` | Full administrative control: user CRUD, account state transitions (`Limitado → Activo → Inactivo`), entrepreneurship & parallel project approval, confidentiality act (`acta`) review, mentor assignment (enforcing 12 h/week and 12 active projects caps), program settings (`configuracion_programa`), institutional reports (CSV/XLSX/PDF), incremental backups (`pg_dump` + hard-link snapshots), and full audit trail (`auditoria_eventos`) |
| **Estudiante (Emprendedor)** | `2` | Self-registration with institutional email, **8-digit OTP verification** (5-min expiry, HMAC-SHA256 storage, max 5 attempts, 60 s cooldown), `Limitado` state gating until admin activation, confidentiality act upload, diagnosis submission, task execution with mandatory evidence upload (≤500 MB, magic-byte MIME validation), advising *request* creation (never direct booking, `BR-002`), and own-resource read/write scope |
| **Docente / Mentor** | `3` | Strictly scoped to **actively assigned entrepreneurships** (`asignaciones.estado = 'activa'`): phase tracing (`Avance de fase`, `Comentario`), task creation/grading/return-with-motive, advising session acceptance/rejection/reproposal with schedule conflict validation, diagnosis review, and event recommendations |
| **Auditor** | `4` | Read-only oversight (P2): zero write permissions (`403 ROLE_NOT_ALLOWED` on all mutating endpoints) and mandatory PII masking (`services/masking.ts`) on document numbers and contact fields |

### 2.2 What Was Just Completed (Repository Split Baseline)
The repository (`https://github.com/Shiro3-s/FINAL-PROJECT-SGEMD.git`) was just split from the monorepo baseline (`feat/mvp-implementation-v1` at `079248a`) into two standalone root branches and verified in Docker:

| Branch | Remote Tracking | Head Commit | Root (`/`) Contents | Verification Baseline |
|---|---|---|---|---|
| **`frontend`** | `origin/frontend` | `122d6e0` | `src/` (64 React views, 26 components, `src/shared/enums.ts`), `public/brand/`, `docs/FRONTEND_BRANCH_MANIFEST.md`, `docs/design-parity.md`, `index.html`, `vite.config.ts`, `tsconfig.json`, `package.json`, `package-lock.json` | `npm ci`, `npm run typecheck`, `npm run build` (`0` errors, `0` npm audit vulnerabilities, 180 Vite modules built into `dist/`) |
| **`backend`** | `origin/backend` | `d9dba88` | `src/` (20 Express 5 modules, middlewares, policies, services, `src/shared/enums.ts`), `database/` (`schema.sql` with 41 tables & 22 `CHECK` constraints, `seed.sql`), `scripts/check-schema.mjs`, `tests/` (21 suites, 292 tests), `storage/`, `backups/`, `docs/BACKEND_BRANCH_MANIFEST.md`, `Dockerfile`, `docker-compose.test.yml`, `vitest.config.ts`, `tsconfig.json`, `package.json`, `package-lock.json` | `npm ci`, `npm run typecheck`, `npm run build`, `npm run check:schema`, `docker build`, and `21/21` test suites (`292/292` tests) passing against PostgreSQL 17 |
| **`feat/mvp-implementation-v1`** | `origin/feat/mvp-implementation-v1` | `079248a` | Historical 3-workspace monorepo baseline | Untouched reference baseline |

---

## 3. TASK TO PERFORM (`Tarea a realizar`)

Execute the following sequential stages using the **`security-audit-runner`** skill. **Do not advance to the next stage until the current stage gate passes.**

---

### Stage 1 — Activate `security-audit-runner` & Audit the `frontend` Branch

1. Checkout the `frontend` branch and synchronize with `origin/frontend`:
   ```bash
   git checkout frontend
   git pull --ff-only origin frontend
   npm ci
   ```
2. Run the **`security-audit-runner`** skill across the `frontend` branch covering all 7 frontend security domains:
   - **F-DOM-01 · Token, Session & Storage Hygiene**:
     - Verify that the session JWT (`sgemd_session`) is never read, decoded, stored, or forwarded via `localStorage`, `sessionStorage`, `indexedDB`, URL query parameters, or JSON response bodies.
     - Verify `src/api/client.ts` uses `credentials: 'same-origin'` (or appropriate cookie credentials) and never attaches raw bearer secrets from browser storage.
     - Verify `localStorage` is restricted strictly to non-sensitive UI preferences (never PII, role IDs used for security decisions, or tokens).
   - **F-DOM-02 · XSS, DOM Injection & Unsafe Rendering**:
     - Scan all `.tsx` and `.ts` files under `src/` for `dangerouslySetInnerHTML`, `innerHTML`, `outerHTML`, `document.write`, `eval`, `new Function`, unvalidated `href="javascript:..."` or user-controlled `window.location` redirects (Open Redirect).
     - Inspect notification deep-links (`Url` from `/api/notifications`), query parameter filters (`?f=`, `useSearchParams`), and file download blobs (`apiDownload`) to confirm safe URL/DOM handling.
   - **F-DOM-03 · Client-Side Route Guards & State Gating**:
     - Audit `src/auth/` / `src/routes/` (`AuthProvider`, `guards.tsx`) to verify that `Limitado` and `Inactivo` account states and role boundaries (`ROLES.ADMIN`, `ROLES.ESTUDIANTE`, `ROLES.DOCENTE`, `ROLES.AUDITOR`) cannot render unauthorized views or leak sensitive cached TanStack Query data across logout/login transitions (`queryClient.clear()` on logout/401).
   - **F-DOM-04 · Upload & Download Client Hardening**:
     - Audit `src/components/Dropzone.tsx` and attachment upload flows (`apiUpload`) for client-side MIME allow-list enforcement (`image/jpeg`, `image/png`, `application/pdf`), file size checks, and safe error surfacing without leaking server internals.
   - **F-DOM-05 · Third-Party & Supply-Chain Security (`npm audit` & External Requests)**:
     - Run `npm audit --json` and verify zero external CDN requests in `index.html`, `src/styles/*.css`, and built `dist/` assets (fonts must remain 100% self-hosted via `@fontsource/inter`).
   - **F-DOM-06 · Build & Source Map Exposure in Production**:
     - Inspect `vite.config.ts` and build artifacts (`dist/`): evaluate whether production source maps (`sourcemap: true`) or environment variable prefixes (`VITE_*`) expose sensitive internal paths or secrets, and harden `vite.config.ts` / `.env.example` as needed.
   - **F-DOM-07 · Privacy & Colombian Ley 1581 de 2012 Compliance**:
     - Scan all tracked files on `frontend` for hardcoded credentials, API keys, or real personal data (names, real institutional emails, real Colombian cédulas/TI/CE, phone numbers).
3. **Remediate Frontend Findings**:
   - Apply code or configuration fixes directly on the `frontend` branch for every actionable finding identified by `security-audit-runner`.
   - Re-run `npm run typecheck` and `npm run build` to confirm zero regressions.
4. **Write the Frontend Security Audit Report**:
   - Create `docs/SECURITY_AUDIT_FRONTEND.md` following the exact specification in §4.1.
5. **Commit and Push to `origin/frontend`**:
   - Stage all frontend fixes and `docs/SECURITY_AUDIT_FRONTEND.md`.
   - Commit using Spanish Conventional Commits (`security(frontend): ...` or `fix(frontend): ...`) and push to `origin/frontend`:
     ```bash
     git status --porcelain
     git push origin frontend
     ```
- **Gate 1**: `npm run typecheck`, `npm run build`, and `npm audit` pass on `frontend`; `docs/SECURITY_AUDIT_FRONTEND.md` is committed; `git status --porcelain` is empty; `origin/frontend` is up to date with local `frontend`.

---

### Stage 2 — Activate `security-audit-runner` & Audit the `backend` Branch

1. Checkout the `backend` branch and synchronize with `origin/backend`:
   ```bash
   git checkout backend
   git pull --ff-only origin backend
   npm ci
   ```
2. Run the **`security-audit-runner`** skill across the `backend` branch covering all 10 backend security domains:
   - **B-DOM-01 · Authentication, JWT & Session Cookie Security**:
     - Audit `src/modules/auth/`, `src/middleware/auth.ts`, and `src/config/env.ts`.
     - Verify `bcryptjs` cost factor (`>= 10`), `jose` JWT signing algorithm (`HS256` pinned explicitly, rejecting `none` or algorithm confusion), 8-hour expiry, minimal payload (`{ id, role }` only), `sgemd_session` cookie attributes (`HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=28800`), and per-request database re-validation of user existence, role, and `estado` (`Activo`, `Limitado`, `Inactivo`).
   - **B-DOM-02 · OTP Cryptography, Brute-Force & Rate-Limiting**:
     - Audit `src/utils/otp.ts`, `src/services/otpCodes.ts`, and `src/middleware/rateLimit.ts`.
     - Verify CSPRNG generation (`crypto.randomInt`), HMAC-SHA256 hashing keyed with `OTP_HMAC_SECRET`, constant-time comparison (`crypto.timingSafeEqual`), 5-minute expiration, max 5 attempts per code, 60-second resend cooldown, single-use enforcement (`usado = true`), and IP rate-limiting on `/auth/login`, `/auth/register`, `/auth/verify-otp`, `/auth/resend-otp`, and `/auth/recover`.
   - **B-DOM-03 · CSRF & Origin Verification (`originCheck.ts` & `helmet`)**:
     - Audit `src/middleware/originCheck.ts` and `src/app.ts`.
     - Verify every mutating request (`POST`, `PUT`, `PATCH`, `DELETE`) enforces strict same-origin validation against `env.APP_ORIGIN` via `Origin` and `Sec-Fetch-Site` headers, and that `helmet` sets restrictive security headers with no permissive `Access-Control-Allow-Origin: *`.
   - **B-DOM-04 · Authorization, BOLA/IDOR & Account State Policy**:
     - Audit all 20 modules under `src/modules/*/` plus `src/policy/accountState.ts`, `src/policy/accountTransitions.ts`, `src/policy/roles.ts`, and `src/services/entrepreneurshipAccess.ts`.
     - Verify deny-by-default role + ownership enforcement on every endpoint (preventing Broken Object Level Authorization / IDOR across students and teachers), `Limitado`/`Inactivo` gating, and complete read-only + PII-masking enforcement for `ROLES.AUDITOR` (`4`).
   - **B-DOM-05 · Input Validation, Mass Assignment & SQL Injection Prevention**:
     - Audit all `schemas.ts` (Zod validation) and SQL queries across `src/modules/*/` and `src/services/*/`.
     - Verify that every SQL query uses `$1, $2...` parameterized placeholders (zero unsafe string concatenation of user input in `ORDER BY`, `LIMIT`, `OFFSET`, or `WHERE`), and that mass-assignment of privileged fields (`rol`, `estado`, `avance`, `puntaje_total`, `usuarios_id_usuarios`) is impossible.
   - **B-DOM-06 · File Upload, Magic-Byte MIME & Path Traversal Hardening**:
     - Audit `src/services/storage.ts`, `src/modules/attachments/`, and `src/modules/acta/`.
     - Verify magic-byte signature inspection (`image/jpeg`, `image/png`, `application/pdf`), random stored filenames, atomic `*.part` streaming with cleanup on error, strict path-traversal containment (`resolve` inside `env.STORAGE_DIR`), and configured size/count limits from `configuracion_programa`.
   - **B-DOM-07 · Backup Engine, Command Execution & Archive Streaming Security**:
     - Audit `src/services/backupFiles.ts` and `src/modules/backups/`.
     - Verify `pg_dump` and `rsync` are invoked via `execFile` / `spawn` argument arrays **without a shell (`shell: false`)**, that `isInsideBackups` blocks directory traversal on deletion/download, that `storage/mail*` and `*.part` are excluded from snapshots, and that every backup creation, verification, download, and export writes to `auditoria_eventos`.
   - **B-DOM-08 · Error Handling, Structured Logging & Secret/PII Leakage**:
     - Audit `src/middleware/error.ts`, `src/config/logger.ts`, `src/services/masking.ts`, and `database/seed.sql`.
     - Verify that 5xx errors return a generic JSON envelope with a correlation ID (never stack traces, SQL errors, or filesystem paths), that logs never record passwords, OTPs, JWTs, or unmasked PII, and that `seed.sql` contains zero real PII (Ley 1581 de 2012).
   - **B-DOM-09 · Dependency & Supply-Chain Vulnerability Audit (`npm audit`)**:
     - Run `npm audit --json` on the `backend` branch.
     - Inspect all reported package advisories (such as transitive advisories in `archiver` / `exceljs` / `pdfkit` / `glob` / `lodash.isequal`), upgrade or apply safe `overrides` in `package.json` where compatible with Node 22 + TypeScript 7 + all 292 tests, and document any residual upstream transitive risk with compensating controls.
   - **B-DOM-10 · Container & Database Schema Security (`Dockerfile` & `database/schema.sql`)**:
     - Audit `Dockerfile` (non-root `USER node`, pinned `postgresql17-client`, minimal Alpine attack surface, file ownership) and run `npm run check:schema` to confirm all 41 tables and 22 `CHECK` constraints match `src/shared/enums.ts`.
3. **Remediate Backend Findings & Verify Against Real PostgreSQL 17**:
   - Apply all code, dependency, or configuration fixes on the `backend` branch.
   - Verify with:
     ```bash
     npm run typecheck
     npm run build
     npm run check:schema
     npm test
     ```
     *(using the PostgreSQL 17 test container from `docker-compose.test.yml`)*.
4. **Write the Backend Security Audit Report**:
   - Create `docs/SECURITY_AUDIT_BACKEND.md` following the exact specification in §4.2.
5. **Commit and Push to `origin/backend`**:
   - Clean any temporary test artifacts in `storage/` or `backups/` (retaining `.gitkeep`).
   - Stage all backend fixes and `docs/SECURITY_AUDIT_BACKEND.md`.
   - Commit using Spanish Conventional Commits (`security(backend): ...` or `fix(backend): ...`) and push to `origin/backend`:
     ```bash
     git status --porcelain
     git push origin backend
     ```
- **Gate 2**: `npm run typecheck`, `npm run build`, `npm run check:schema`, and the full integration test suite pass on `backend`; `docs/SECURITY_AUDIT_BACKEND.md` is committed; `git status --porcelain` is empty; `origin/backend` is up to date with local `backend`.

---

## 4. DELIVERABLE FORMAT SPECIFICATION (`Formato de entrega`)

All deliverables must be written in **English** in GitHub-Flavored Markdown (`.md`).

### 4.1 Deliverable 1 — `docs/SECURITY_AUDIT_FRONTEND.md` (Committed & Pushed to `origin/frontend`)
Must contain:
1. **Executive Summary & Audit Metadata**: Branch (`frontend`), base commit, audited commit, timestamp, `security-audit-runner` version/scope, overall risk rating, and summary counts by severity (`Critical`, `High`, `Medium`, `Low`, `Informational`).
2. **Domain-by-Domain Audit Matrix (`F-DOM-01` through `F-DOM-07`)**: Status (`PASS`, `HARDENED`, `MITIGATED`), exact files and line numbers inspected, and technical evidence.
3. **Findings & Remediations Ledger**: For every finding (`FE-SEC-001`, `FE-SEC-002`, ...):
   - Severity & CVSS v3.1 / OWASP Top 10 / CWE mapping
   - Location (`file:line`)
   - Vulnerability / Weakness Description & Proof of Concept
   - Remediation Applied (exact diff summary)
   - Verification Command & Result
4. **Supply-Chain & Dependency Audit (`npm audit`)**: Output before and after remediation, plus confirmation of zero external runtime CDN calls.
5. **Vercel Deployment Security Checklist**: Recommended `vercel.json` security headers (`Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`).

### 4.2 Deliverable 2 — `docs/SECURITY_AUDIT_BACKEND.md` (Committed & Pushed to `origin/backend`)
Must contain:
1. **Executive Summary & Audit Metadata**: Branch (`backend`), base commit, audited commit, timestamp, `security-audit-runner` scope, overall risk rating, and summary counts by severity (`Critical`, `High`, `Medium`, `Low`, `Informational`).
2. **Domain-by-Domain Audit Matrix (`B-DOM-01` through `B-DOM-10`)**: Mapping directly against the 24 security controls of `MASTER_IMPLEMENTATION_PROMPT.md` §15, with exact `file:line` references and corresponding integration test IDs (`T01`–`T40`).
3. **Findings & Remediations Ledger**: For every finding (`BE-SEC-001`, `BE-SEC-002`, ...):
   - Severity & CVSS v3.1 / OWASP API Security Top 10 / CWE mapping
   - Location (`file:line` or dependency chain)
   - Vulnerability / Weakness Description & Attack Vector
   - Remediation Applied (code fix or dependency override/upgrade)
   - Verification Command & Test Suite Result
4. **Supply-Chain & Container Security Audit**: `npm audit` analysis before and after remediation, plus `Dockerfile` security posture review.
5. **Supabase & Production Hardening Checklist**: SSL connection enforcement (`?sslmode=require`), least-privilege database role (non-superuser), secret rotation policy (`JWT_SECRET`, `OTP_HMAC_SECRET`), and `APP_ORIGIN` pairing with Vercel.

### 4.3 Deliverable 3 — Consolidated Response & Local Master Summary (`SECURITY_AUDIT_MASTER_REPORT.md`)
Produce a consolidated English summary report in your final response (and save it locally as `SECURITY_AUDIT_MASTER_REPORT.md` excluded via `.git/info/exclude` so branch working trees remain clean) summarizing:
- Branch commits pushed to `origin/frontend` and `origin/backend`
- Summary table of all `FE-SEC-*` and `BE-SEC-*` findings and their remediation status
- Verification checklist table (`SA01`–`SA12`)

---

## 5. REFERENCE EXAMPLES (`Ejemplo de cómo debe verse el resultado`)

Use the following structure and engineering precision (modeled after `MASTER_IMPLEMENTATION_PROMPT.md` §15 and §18) when writing your audit ledgers and commit messages:

### 5.1 Example — Domain Audit Matrix Row (`docs/SECURITY_AUDIT_BACKEND.md`)

| Domain ID | Control Area (§15 Reference) | Inspected Files | Security Invariant Verified | Automated Test Proof | Status |
|---|---|---|---|---|---|
| `B-DOM-01` | Session Cookie & Per-Request Lookup | `src/modules/auth/session.ts:14-48`, `src/middleware/auth.ts:15-52` | `sgemd_session` cookie enforces `HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=28800`; JWT payload contains only `{ id, role }`; `auth` middleware queries `usuarios` on every request and enforces `policy/accountState.ts` immediately | `tests/auth.test.ts` (`T02`, `T04`), `tests/users.test.ts` (`T13`) | `PASS` |
| `B-DOM-06` | Upload MIME & Path Traversal | `src/services/storage.ts:42-168`, `src/modules/attachments/service.ts:28-95` | Content magic-bytes inspected against `TIPOS_MIME_ADJUNTO` (`image/jpeg`, `image/png`, `application/pdf`); streamed to `*.part` before atomic rename; resolved path verified inside `env.STORAGE_DIR` | `tests/attachments.test.ts` (`T19`, `T40`) | `PASS` |

### 5.2 Example — Finding & Remediation Entry

```markdown
#### `BE-SEC-001` — Explicit Algorithm Pinning in JWT Verification (`CWE-347` / OWASP API2:2023)
- **Severity**: Low (Defense-in-Depth Hardening)
- **Location**: `src/modules/auth/session.ts:38`
- **Description**: `jwtVerify(token, secretKey)` should explicitly pin `algorithms: ['HS256']` in options to prevent any algorithm confusion if key material handling ever changes.
- **Remediation Applied**: Added `{ algorithms: ['HS256'] }` to `jwtVerify` options in `src/modules/auth/session.ts`.
- **Verification**: `npm run typecheck && npx vitest run tests/auth.test.ts` — 100% PASS.
```

### 5.3 Example — Branch Commit & Push Convention

- **On `frontend` branch (`origin/frontend`)**:
  ```text
  security(frontend): complete security-audit-runner audit and hardening report

  - Execute F-DOM-01..F-DOM-07 security audit with security-audit-runner
  - Harden production Vite build configuration and verify zero external CDN leaks
  - Add docs/SECURITY_AUDIT_FRONTEND.md with full finding ledger and Vercel CSP headers
  - Verify npm run typecheck, npm run build, and npm audit (0 vulnerabilities)
  ```
- **On `backend` branch (`origin/backend`)**:
  ```text
  security(backend): complete security-audit-runner audit, dependency hardening, and report

  - Execute B-DOM-01..B-DOM-10 security audit with security-audit-runner
  - Apply security remediations and dependency overrides while preserving 292/292 tests
  - Add docs/SECURITY_AUDIT_BACKEND.md mapped to §15 controls and T01-T40 test catalog
  - Verify npm run typecheck, npm run build, npm run check:schema, and Vitest suite
  ```

---

## 6. CONSTRAINTS & NON-NEGOTIABLE RULES (`Restricciones`)

1. **Mandatory Use of `security-audit-runner`**: You must load and follow the `security-audit-runner` skill methodology for both branches. Do not skip static analysis, dependency auditing, or access-control verification.
2. **Strict English Deliverable Language**: All generated audit reports (`docs/SECURITY_AUDIT_FRONTEND.md`, `docs/SECURITY_AUDIT_BACKEND.md`, and your final response) must be written in clear, technical **English**. (User-facing UI copy and canonical enum strings in the application code itself must remain in **Spanish (Colombia)** per project rules!).
3. **Strict Branch Isolation**:
   - Never commit backend files or `SECURITY_AUDIT_BACKEND.md` onto the `frontend` branch.
   - Never commit frontend files or `SECURITY_AUDIT_FRONTEND.md` onto the `backend` branch.
   - Never modify or push to `feat/mvp-implementation-v1` or `main`.
4. **Zero Functional or Visual Regression**:
   - Do not alter any API endpoint path, HTTP status code contract, database table/column name in `database/schema.sql`, Spanish enum string in `src/shared/enums.ts`, or CSS hex token in `src/styles/tokens.css`.
   - Any security fix that breaks `npm run typecheck`, `npm run build`, `npm run check:schema`, or any of the 21 backend test suites is invalid and must be corrected before committing.
5. **No Secrets or Runtime Artifacts in Git**:
   - Never commit `.env`, `node_modules/`, `dist/`, test mail files (`storage/mail*`), uploaded test files (`storage/*`), or backup dumps (`backups/*`) to either branch.
   - Always verify `git status --porcelain` is empty before and after pushing each branch to `origin`.
6. **No Force-Pushing (`git push --force` is forbidden)**:
   - Push cleanly as fast-forward commits onto `origin/frontend` and `origin/backend`.

---

## 7. VERIFICATION CHECKLIST (`SA01`–`SA12`)

Before declaring the audit complete, verify all 12 gates:

- [ ] **SA01 (`security-audit-runner` Execution)**: `security-audit-runner` workflow executed across both `frontend` and `backend` branches.
- [ ] **SA02 (`frontend` Static & DOM Audit)**: All 7 frontend domains (`F-DOM-01`…`F-DOM-07`) audited and remediated on `frontend`.
- [ ] **SA03 (`frontend` Build & Typecheck Gate)**: `npm run typecheck` and `npm run build` on `frontend` exit with code `0` after hardening.
- [ ] **SA04 (`frontend` Report Committed & Pushed)**: `docs/SECURITY_AUDIT_FRONTEND.md` (in English) is committed and pushed to `origin/frontend`.
- [ ] **SA05 (`backend` 10-Domain Audit)**: All 10 backend domains (`B-DOM-01`…`B-DOM-10`) audited against §15 security baseline and remediated on `backend`.
- [ ] **SA06 (`backend` Build, Typecheck & Schema Gate)**: `npm run typecheck`, `npm run build`, and `npm run check:schema` on `backend` exit with code `0` after hardening.
- [ ] **SA07 (`backend` Real PostgreSQL 17 Integration Suite)**: Full integration test suite (`npm test`) passes against PostgreSQL 17 after all backend security remediations.
- [ ] **SA08 (`backend` Report Committed & Pushed)**: `docs/SECURITY_AUDIT_BACKEND.md` (in English) is committed and pushed to `origin/backend`.
- [ ] **SA09 (Ley 1581 de 2012 & Secret Scan)**: Zero hardcoded secrets, tokens, or real PII exist in tracked files on `frontend` or `backend`.
- [ ] **SA10 (Supply-Chain Audit)**: `npm audit` executed and documented on both `frontend` and `backend`.
- [ ] **SA11 (Git Hygiene)**: `git status --porcelain` is empty on `frontend`, `backend`, and `feat/mvp-implementation-v1`.
- [ ] **SA12 (Remote Sync Verification)**: `git rev-parse frontend == git rev-parse origin/frontend` and `git rev-parse backend == git rev-parse origin/backend`.
