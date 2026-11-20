# Auditorías de Seguridad — SGEMD MVP (`docs/security-audits`)

> **Metodología**: `security-audit-runner` (7 dominios Frontend + 10 dominios Backend)  
> **Ramas Auditadas**: `front/production` (`25f779e`) y `back/production` (`e9f857e`)  
> **Postura Final**: **BAJO RIESGO / LISTO PARA PRODUCCIÓN** (`0` vulnerabilidades abiertas · `0` vulnerabilidades `npm audit` en ambas ramas · `292/292` pruebas aprobadas en PostgreSQL 17)

---

## Entregables Incluidos en esta Rama

| Archivo | Descripción |
|---|---|
| [`SECURITY_AUDIT_FRONTEND.md`](./SECURITY_AUDIT_FRONTEND.md) | Reporte completo en inglés de la auditoría y remediación de la rama Frontend (`F-DOM-01`..`F-DOM-07`, hallazgos `FE-SEC-001`..`FE-SEC-006`, checklist de cabeceras CSP/HSTS para Vercel). |
| [`SECURITY_AUDIT_BACKEND.md`](./SECURITY_AUDIT_BACKEND.md) | Reporte completo en inglés de la auditoría y remediación de la rama Backend (`B-DOM-01`..`B-DOM-10`, hallazgos `BE-SEC-001`..`BE-SEC-007`, remediación `7 → 0` en `npm audit`, matriz §15 / `T01`–`T40` y checklist para Supabase). |
| [`SECURITY_AUDIT_MASTER_REPORT.md`](./SECURITY_AUDIT_MASTER_REPORT.md) | Reporte maestro consolidado de ambas ramas y matriz de puertas de verificación (`SA01`–`SA12`). |
| [`MASTER_SECURITY_AUDIT_PROMPT.md`](./MASTER_SECURITY_AUDIT_PROMPT.md) | Master Prompt estructurado (en inglés) que define el rol, contexto, dominios de auditoría con `security-audit-runner`, formato de entrega, ejemplos y restricciones. |
| [`PRESENTACION_AUDITORIA_SGEMD.html`](./PRESENTACION_AUDITORIA_SGEMD.html) | Presentación ejecutiva interactiva en HTML autocontenido (11 diapositivas con paleta institucional UNIMINUTO/SGEMD, gráficos SVG, vista general `G`, pantalla completa `F` y exportación a PDF). |

---

## Resumen de Resultados

| Rama de Producción | Commit Auditado | Dominios | Hallazgos Cerrados | `npm audit` | Pruebas |
|---|---|---|---|---|---|
| `front/production` | `25f779e` | `7 / 7` | `6 / 6` (`FE-SEC-001`..`006`) | **`0`** (`85` pkgs) | `typecheck` + `vite build` PASS |
| `back/production` | `e9f857e` | `10 / 10` | `7 / 7` (`BE-SEC-001`..`007`) | **`0`** (`7 → 0`) | `292 / 292` tests PASS + `check:schema` |
