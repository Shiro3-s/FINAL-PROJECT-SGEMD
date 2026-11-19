# Manifiesto de Separación — Rama `frontend` (SGEMD MVP)

> **Rama**: `frontend`  
> **Commit Base**: `079248a` (`feat/mvp-implementation-v1`)  
> **Destino de Despliegue**: Vercel (React 19 + Vite 8 SPA en la raíz `/`)

---

## 1. Árbol de Directorios de la Rama `frontend`

```text
/ (root of `frontend` branch)
├── public/
│   └── brand/
│       ├── logo-blanco.png
│       └── logo-color.png
├── src/
│   ├── shared/
│   │   ├── enums.ts                  # Cadenas canónicas §7.2 en español y tuplas de catálogos
│   │   └── index.ts                  # Re-exporta enums.ts (destino del alias `@sgemd/shared`)
│   ├── api/
│   │   ├── client.ts                 # Cliente HTTP/XHR/SSE para `/api/*`
│   │   └── types.ts                  # Interfaces DTO del frontend
│   ├── components/                   # 26 componentes UI institucionales
│   ├── context/                      # AuthContext.tsx, ToastContext.tsx
│   ├── hooks/                        # Custom React hooks
│   ├── lib/                          # Formateadores (`America/Bogota`) y stateMap.ts
│   ├── pages/
│   │   ├── auth/                     # Login, Registro, VerificarOtp, Recuperar
│   │   ├── estudiante/               # 19 vistas de estudiante + Acta
│   │   ├── docente/                  # 20 vistas de docente
│   │   ├── admin/                    # 19 vistas de administrador + revisión de Actas
│   │   └── shared/                   # Vistas compartidas entre roles
│   ├── queries/                      # Hooks de TanStack Query por módulo de dominio
│   ├── routes/                       # AppRoutes, RequireAuth, RequireRole, RequireActive
│   ├── styles/                       # tokens.css (paleta 6 hex), fonts.css (@fontsource/inter), base, layout
│   ├── App.tsx
│   └── main.tsx
├── docs/
│   ├── FRONTEND_BRANCH_MANIFEST.md   # Este documento
│   └── design-parity.md              # Registro de paridad visual de las 64 vistas
├── index.html
├── vite.config.ts                    # Configuración Vite 8 standalone con alias `@sgemd/shared`
├── tsconfig.json                     # Configuración TypeScript 7 standalone (sin `../tsconfig.base.json`)
├── package.json                      # Manifiesto standalone `@sgemd/frontend`
├── package-lock.json                 # Lockfile standalone
├── .env.example                      # Plantilla de variables de entorno del frontend
├── .gitignore
└── README.md                         # Guía standalone de instalación y compilación
```

---

## 2. Desacoplamiento de `@sgemd/shared` y `tsconfig.base.json`

1. **Inlining de `@sgemd/shared`**:
   - Se copiaron íntegramente `shared/src/enums.ts` y `shared/src/index.ts` dentro de `src/shared/enums.ts` y `src/shared/index.ts` sin alterar ninguna cadena canónica en español ni tupla de catálogo.
2. **Resolución en TypeScript (`/tsconfig.json`)**:
   - Se eliminó `"extends": "../tsconfig.base.json"` y se fusionaron directamente las banderas estrictas (`strict: true`, `noImplicitOverride: true`, `noUnusedLocals: true`, `noUnusedParameters: true`, `noFallthroughCasesInSwitch: true`, `forceConsistentCasingInFileNames: true`, `esModuleInterop: true`, `resolveJsonModule: true`, `skipLibCheck: true`).
   - Se declaró `"paths": { "@sgemd/shared": ["./src/shared/index.ts"] }` en `compilerOptions`, permitiendo que todos los `import { ... } from '@sgemd/shared'` existentes en `src/` compilen sin modificar ningún componente.
3. **Resolución en Vite 8 (`/vite.config.ts`)**:
   - Se configuró `resolve.alias`:
     ```ts
     '@sgemd/shared': fileURLToPath(new URL('./src/shared/index.ts', import.meta.url))
     ```
4. **Autonomía de `/package.json`**:
   - Se eliminó la dependencia de workspace `"@sgemd/shared": "*"` de `dependencies`.
   - Se incorporó `"typescript": "7.0.2"` y `"@types/node": "26.6.5"` en `devDependencies`, generando un `package-lock.json` autónomo en la raíz.

---

## 3. Directorios y Archivos Podados en la Rama `frontend`

Durante el aislamiento de la rama se eliminaron todos los artefactos ajenos al cliente web:

- **Backend y Base de Datos**: `backend/`, `shared/`, `database/`, `scripts/`, `storage/`, `backups/`
- **Infraestructura Docker y Proxy**: `caddy/`, `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.test.yml`, `Makefile`, `tsconfig.base.json`
- **Prototipos HTML y Scaffolds Legados**: `prototype/`, `Config-admin/`, `.stitch/`, `core/`, `agents/`, `skills/`, `interfaces/`, `config/`, `tools/`, `evaluations/`, `crear_estructura_framework.py`
- **Documentos Históricos/Backend**: `CAMBIOS_v1.3.md`, `CORRECCIONES-VISTAS-ESTUDIANTE.md`, `PROTOTIPO-STITCH.md`, `MASTER_IMPLEMENTATION_PROMPT.md`, y documentos de backend/arquitectura en `docs/` (conservando únicamente `docs/design-parity.md` y `docs/FRONTEND_BRANCH_MANIFEST.md`).

---

## 4. Comandos Verificados y Tamaños del Bundle de Producción

| Comando | Código de Salida | Resultado |
|---|---|---|
| `npm install` | `0` | Lockfile standalone generado sin referencias a workspaces padres |
| `npm run typecheck` | `0` | `tsc -p tsconfig.json --noEmit` sin errores en las 64 vistas |
| `npm run build` | `0` | Bundle de producción generado en `dist/` (180 módulos transformados) |

### Artefactos Generados en `dist/`
- `dist/index.html` (`0.51 kB` · gzip `0.33 kB`)
- `dist/assets/index-*.css` (`47.46 kB` · gzip `9.01 kB`)
- `dist/assets/index-*.js` (`560.84 kB` · gzip `151.74 kB`)
- `dist/assets/inter-latin-*.woff2` / `.woff` (10 archivos de fuentes autoalojadas `@fontsource/inter`, cero peticiones a CDNs externos)

---

## 5. Lista de Preparación para Despliegue en Vercel (Next-Step Readiness Checklist)

- [x] `package.json`, `package-lock.json`, `vite.config.ts`, `tsconfig.json` e `index.html` ubicados en la raíz `/` de la rama `frontend`.
- [x] Cero referencias a `../` en archivos de configuración o código fuente.
- [x] `npm run build` emite `dist/index.html` y `dist/assets/*` sin depender de `shared/` ni `backend/`.
- [ ] En la fase de despliegue en Vercel: configurar rewrite `/api/:path*` en `vercel.json` (o `VITE_API_BASE_URL`) apuntando al dominio público del backend y definir las cabeceras de seguridad CSP/HSTS correspondientes.
