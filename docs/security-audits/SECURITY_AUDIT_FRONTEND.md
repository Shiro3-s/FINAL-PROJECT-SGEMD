# SGEMD Security Audit & Hardening Report — `frontend` Branch

> **Branch**: `frontend` (`origin/frontend`)  
> **Baseline Commit**: `122d6e0` (branched from `feat/mvp-implementation-v1` at `079248a`)  
> **Methodology / Skill**: `security-audit-runner` (7-Domain Client-Side & Supply-Chain Security Audit)  
> **Audit Date**: 2026-11-19  
> **Target Environment**: Vercel (Standalone React 19.3.1 + Vite 8.3.5 + TypeScript 7.0.2 SPA)

---

## 1. Executive Summary & Audit Metadata

A comprehensive security audit and defense-in-depth hardening pass was executed on the standalone `frontend` branch of **SGEMD (Sistema de Gestión de Emprendimiento Minuto de Dios)** using the **`security-audit-runner`** workflow.

The audit covered all 64 institutional React views, 26 shared UI components, the HTTP/XHR/SSE client layer (`src/api/client.ts`), client-side authentication and account-state route guards (`src/auth/`), TanStack Query cache lifecycle (`src/queries/`), Vite 8 production build output (`vite.config.ts`), and npm dependency supply-chain integrity (`npm audit`).

### 1.1 Findings Summary by Severity

| Severity | Count Found | Remediated / Hardened | Open / Unresolved |
|---|---|---|---|
| **Critical** | `0` | `0` | `0` |
| **High** | `0` | `0` | `0` |
| **Medium** | `1` | `1` (`FE-SEC-001`) | `0` |
| **Low** | `3` | `3` (`FE-SEC-002`, `FE-SEC-003`, `FE-SEC-004`) | `0` |
| **Informational** | `2` | `2` (`FE-SEC-005`, `FE-SEC-006` — Verified by Design) | `0` |
| **Total** | **`6`** | **`6` (100%)** | **`0`** |

**Overall Post-Remediation Risk Rating**: **LOW / PRODUCTION-READY** (`0` open code vulnerabilities, `0` `npm audit` dependency vulnerabilities).

---

## 2. Domain-by-Domain Audit Matrix (`F-DOM-01` through `F-DOM-07`)

| Domain ID | Security Domain | Inspected Files & Lines | Security Invariant Verified | Status |
|---|---|---|---|---|
| **`F-DOM-01`** | Token, Session & Browser Storage Hygiene | `src/api/client.ts:61-85`, `src/api/client.ts:123-172`, `src/api/client.ts:249-273`, `src/auth/AuthProvider.tsx:24-41` | Zero occurrences of `localStorage`, `sessionStorage`, `indexedDB`, or `document.cookie` across the entire `src/` tree. The session credential is managed exclusively via the server-set `HttpOnly; Secure; SameSite=Strict` cookie (`sgemd_session`). `fetch` uses `credentials: 'same-origin'`, `XMLHttpRequest` uses `withCredentials = true`, and `EventSource` uses `withCredentials: true`. | `PASS` |
| **`F-DOM-02`** | XSS, DOM Injection & Unsafe URI / Redirect Handling | `src/components/Icon.tsx:7-91`, `src/pages/shared/EventDetailPage.tsx:136-148`, `src/pages/auth/LoginPage.tsx:45-53`, `src/pages/shared/NotificationsPage.tsx:51`, `src/components/NotificationDrawer.tsx:40` | Zero user-controlled `dangerouslySetInnerHTML`, `innerHTML`, `eval`, or `document.write`. The sole `dangerouslySetInnerHTML` in `Icon.tsx:89` renders compile-time frozen SVG constants (`ICON_PATHS as const`). External event links (`event.enlace`) and internal navigation targets (`state.from`, `notification.url`) were hardened against `javascript:` schemes and protocol-relative open redirects (`FE-SEC-001`, `FE-SEC-002`). | `HARDENED` |
| **`F-DOM-03`** | Client-Side Route Guards, Account State Gating & Cache Isolation | `src/auth/guards.tsx:33-123`, `src/queries/session.ts:52-76`, `src/App.tsx:1-220` | `<RequireAuth>`, `<RequireRole>`, and `<RequireActive>` enforce role boundaries (`admin`, `estudiante`, `docente`; `auditor` blocked at `/403`) and account-state gating (`Limitado` and `Inactivo` restricted to profile, notifications, and student `acta`). Both `useLogout` and `useLogin` now execute `queryClient.clear()` to prevent cross-session cache leakage (`FE-SEC-003`). | `HARDENED` |
| **`F-DOM-04`** | Upload & Download Client Hardening | `src/components/Dropzone.tsx:22-82`, `src/api/client.ts:123-233` | File uploads stream via `FormData` and `XMLHttpRequest` with abort-signal cleanup and structured `ApiError` handling. Binary downloads (`apiDownload`, `saveDownload`) parse RFC 5987 `filename*=UTF-8''` headers safely, create short-lived `blob:` object URLs on the application origin, and revoke them within `1000 ms`. | `PASS` |
| **`F-DOM-05`** | Third-Party Supply-Chain & External Network Zero-Leakage | `package.json`, `package-lock.json`, `index.html`, `src/styles/fonts.css`, `src/styles/tokens.css` | `npm audit` reports **`0` vulnerabilities** across all 85 audited packages. Typography (`@fontsource/inter`) and institutional palette tokens (`#ffd300`, `#ffffff`, `#162644`, `#051533`, `#004a93`, `#bbbbbb`) are 100% self-hosted; zero runtime requests are made to Google Fonts or external CDNs. | `PASS` |
| **`F-DOM-06`** | Production Build & Source Map Exposure | `vite.config.ts:21-24`, `tsconfig.json` | Hardened `vite.config.ts` so production builds do not emit the `2.71 MB` `dist/assets/index-*.js.map` source map file unless `VITE_SOURCEMAP=true` is explicitly set (`FE-SEC-004`). | `HARDENED` |
| **`F-DOM-07`** | Privacy & Colombian Ley 1581 de 2012 Compliance | `.gitignore`, `.env.example`, `src/**`, `docs/**` | Zero hardcoded API keys, JWT secrets, passwords, or real PII (names, document numbers, phone numbers, real institutional emails) exist in any tracked file on the `frontend` branch. `.gitignore` explicitly blocks `.env`, `.env.*`, and unversioned local area folders (`docs/centroProgresa/`, `docs/estudiante/`). | `PASS` |

---

## 3. Findings & Remediations Ledger

### `FE-SEC-001` — Unvalidated URI Scheme and Missing `noopener` on External Event Anchor (`CWE-79` / `CWE-1022` / OWASP A03:2021)
- **Severity**: Medium
- **Location**: `src/pages/shared/EventDetailPage.tsx:138-144`
- **Description**: In `EventDetailPage.tsx`, `event.enlace` was rendered directly into `<a href={event.enlace} target="_blank" rel="noreferrer">`. If an event record ever contained a non-HTTP URI scheme (such as `javascript:` or `data:`), clicking the link could execute script in the victim's origin context. Additionally, `rel="noopener noreferrer"` should be declared explicitly.
- **Remediation Applied**:
  ```tsx
  value: event.enlace ? (
    /^https?:\/\//i.test(event.enlace) ? (
      <a href={event.enlace} target="_blank" rel="noopener noreferrer">
        {event.enlace}
      </a>
    ) : (
      event.enlace
    )
  ) : (
    '—'
  ),
  ```
- **Verification**: `npm run typecheck && npm run build` — **PASS (`0` errors)**.

---

### `FE-SEC-002` — Internal Path Validation on Dynamic Post-Login and Notification Navigation (`CWE-601` / OWASP A01:2021)
- **Severity**: Low (Defense-in-Depth Hardening)
- **Location**: `src/pages/auth/LoginPage.tsx:45`, `src/pages/shared/NotificationsPage.tsx:51`, `src/components/NotificationDrawer.tsx:40`
- **Description**: `LoginPage.tsx` navigated to `state?.from` after login, and `NotificationsPage.tsx` / `NotificationDrawer.tsx` navigated to `notification.url` (`if (url) navigate(url)`). Without verifying that the path starts with a single `/` and not `//` (protocol-relative URL), a tampered history state or malformed notification URL could trigger an unexpected navigation target.
- **Remediation Applied**:
  - Added strict single-slash internal path validation (`url.startsWith('/') && !url.startsWith('//')`) in `LoginPage.tsx`, `NotificationsPage.tsx`, and `NotificationDrawer.tsx`.
- **Verification**: `npm run typecheck && npm run build` — **PASS (`0` errors)**.

---

### `FE-SEC-003` — Cross-Session TanStack Query Cache Purge on Login (`CWE-200` / OWASP A04:2021)
- **Severity**: Low (Defense-in-Depth Hardening)
- **Location**: `src/queries/session.ts:57-61`
- **Description**: While `useLogout()` properly executed `queryClient.clear()`, `useLogin()` only invalidated and refetched `sessionKeys.me` (`['session', 'me']`). On a shared institutional workstation where User A's session cookie expired and User B logged in without an explicit logout click, stale cached queries from User A could briefly remain in memory until refetched.
- **Remediation Applied**:
  - Added `queryClient.clear()` at the start of `useLogin`'s `onSuccess` handler in `src/queries/session.ts` before refetching `sessionKeys.me`.
- **Verification**: `npm run typecheck && npm run build` — **PASS (`0` errors)**.

---

### `FE-SEC-004` — Unconditional Production Source Map Emission (`CWE-540` / OWASP A05:2021)
- **Severity**: Low (Production Hardening)
- **Location**: `vite.config.ts:21-24`
- **Description**: `build.sourcemap` was hardcoded to `true`, causing every production build (`npm run build`) to emit a `2.71 MB` `dist/assets/index-*.js.map` file containing the entire TypeScript source tree into the publicly served `dist/` folder.
- **Remediation Applied**:
  - Updated `vite.config.ts` to `sourcemap: process.env.VITE_SOURCEMAP === 'true'`, disabling public source map emission by default in production builds while allowing opt-in debugging when `VITE_SOURCEMAP=true`.
- **Verification**: `npm run build` — confirmed `dist/assets/` emits `index-CZlxSetv.js` (`560.99 kB`) and `index-CmusGUV7.css` (`47.46 kB`) with **zero `.js.map` files** in `dist/`.

---

### `FE-SEC-005` — Static SVG Path Rendering via `dangerouslySetInnerHTML` (`src/components/Icon.tsx:89`)
- **Severity**: Informational (Verified Safe by Design)
- **Location**: `src/components/Icon.tsx:7-91`
- **Audit Assessment**: `Icon.tsx` uses `dangerouslySetInnerHTML={{ __html: ICON_PATHS[name] }}` where `name` is strongly typed as `keyof typeof ICON_PATHS` and `ICON_PATHS` is a compile-time `as const` dictionary of literal SVG `<path>`/`<rect>`/`<circle>` primitives with zero runtime or user-supplied input. No remediation required.

---

### `FE-SEC-006` — SSE Real-Time Notification Stream (`src/api/client.ts:249-273`)
- **Severity**: Informational (Verified Safe by Design)
- **Location**: `src/api/client.ts:249-273`, `src/components/AppShell.tsx`
- **Audit Assessment**: Per `MASTER_IMPLEMENTATION_PROMPT.md` §15 and `T21`, the SSE `/api/notifications/stream` channel transmits only `{ id, tipo, unreadCount }` metadata and never carries raw notification message text over the event stream; the client invalidates the notifications query and fetches sanitized records via `GET /api/notifications`.

---

## 4. Supply-Chain & Dependency Audit (`npm audit`)

Executed at the standalone `frontend` root (`/`):

```text
$ npm audit
found 0 vulnerabilities
```

- **Total Audited Packages**: `85` (`84` dependencies/devDependencies + root)
- **Vulnerabilities**: `0 Critical`, `0 High`, `0 Moderate`, `0 Low`
- **External Runtime CDN Dependencies**: `0` (verified via static grep across `index.html`, `src/`, and compiled `dist/assets/*`).

---

## 5. Vercel Deployment Security Checklist

When connecting the `frontend` branch to **Vercel**, include the following security headers in `vercel.json` to preserve parity with the institutional Caddy security posture (`MASTER_IMPLEMENTATION_PROMPT.md` §15):

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; font-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=63072000; includeSubDomains; preload"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        }
      ]
    }
  ]
}
```