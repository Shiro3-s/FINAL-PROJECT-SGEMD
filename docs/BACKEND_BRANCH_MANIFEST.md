# Manifiesto de Separación — Rama `backend` (SGEMD MVP)

> **Rama**: `backend`  
> **Commit Base**: `079248a` (`feat/mvp-implementation-v1`)  
> **Destino de Despliegue**: Supabase PostgreSQL 17 + Contenedor/Runtime Node.js 22 Express 5 en la raíz (`/`)

---

## 1. Árbol de Directorios de la Rama `backend`

```text
/ (root of `backend` branch)
├── src/
│   ├── shared/
│   │   ├── enums.ts                  # Cadenas canónicas §7.2 en español y tuplas de catálogos
│   │   └── index.ts                  # Re-exporta enums.ts (`./enums.js`)
│   ├── adapters/
│   │   └── mailer/                   # fileMailer.ts, smtpMailer.ts, index.ts
│   ├── config/
│   │   ├── env.ts                    # Validación Zod de variables de entorno (carga `./.env`)
│   │   └── logger.ts                 # Logger estructurado Pino
│   ├── db/
│   │   └── pool.ts                   # pg.Pool, query(), withTransaction(), afterCommit()
│   ├── jobs/
│   │   ├── inactivity.job.ts         # Job de inactividad de 90 días (BR-005)
│   │   ├── overdueTasks.job.ts       # Job de notificación de tareas vencidas
│   │   └── scheduler.ts              # Planificador de jobs en segundo plano
│   ├── middleware/                   # accountState, auth, error, originCheck, rateLimit, role, validate
│   ├── modules/                      # 20 módulos de dominio (auth, users, entrepreneurship, assignments, etc.)
│   ├── policy/                       # accountState.ts, accountTransitions.ts, roles.ts
│   ├── services/                     # audit, backupFiles, catalogs, codes, email, evidence, masking, notify, etc.
│   ├── types/
│   │   └── express.d.ts
│   ├── utils/                        # AppError, asyncHandler, dates, otp, params, password, respond
│   ├── app.ts                        # Fábrica de aplicación Express 5
│   └── server.ts                     # Servidor HTTP y apagado controlado
├── database/
│   ├── schema.sql                    # 41 tablas PostgreSQL 17 y 22 restricciones CHECK
│   ├── seed.sql                      # 14 catálogos, 22 preguntas de diagnóstico, 18 parámetros y datos demo
│   └── README.md                     # Instrucciones de inicialización, reinicio y restauración de BD
├── scripts/
│   └── check-schema.mjs              # Verifica que database/schema.sql coincida con src/shared/enums.ts
├── tests/                            # 21 suites de integración/unidad Vitest + Supertest (285 tests)
├── storage/
│   └── .gitkeep
├── backups/
│   └── .gitkeep
├── docs/
│   ├── BACKEND_BRANCH_MANIFEST.md    # Este documento
│   ├── api.md                        # Contrato de la API REST implementada
│   ├── decisions.md                  # Registro de ADRs y decisiones técnicas
│   ├── diagrama-clases.md            # Especificación de 27 clases y 14 catálogos verificada por check-schema.mjs
│   ├── traceability.md               # Trazabilidad FR/NFR/BR -> módulo -> test
│   └── verification.md               # Bitácora de verificación de etapas
├── Dockerfile                        # Dockerfile standalone del backend (construye desde `/`)
├── docker-compose.test.yml           # Servicio PostgreSQL 17 efímero para `npm test`
├── vitest.config.ts                  # Configuración standalone de Vitest 5
├── tsconfig.json                     # Configuración standalone de TypeScript 7 (sin `../tsconfig.base.json`)
├── package.json                      # Manifiesto standalone `@sgemd/backend`
├── package-lock.json                 # Lockfile standalone
├── .env.example                      # Plantilla de variables de entorno del backend
├── .gitignore
└── README.md                         # Guía standalone de configuración, pruebas y base de datos
```

---

## 2. Desacoplamiento de `@sgemd/shared` y `tsconfig.base.json`

1. **Inlining de `@sgemd/shared` dentro de `src/shared/`**:
   - Se copiaron íntegramente `shared/src/enums.ts` y `shared/src/index.ts` en `src/shared/enums.ts` y `src/shared/index.ts`.
   - Para garantizar compatibilidad 100 % nativa con Node.js 22 ESM (`NodeNext`) tanto en `tsc`, `tsx`, `vitest` como en ejecución compilada (`node dist/server.js`) sin depender de enlaces simbólicos en `node_modules`:
     - Los 26 archivos en `src/modules/<modulo>/*.ts` importan directamente `'../../shared/index.js'`.
     - Los 6 archivos en `src/policy/*.ts` y `src/services/*.ts` importan directamente `'../shared/index.js'`.
   - Al ejecutar `npm run build`, TypeScript emite `dist/shared/enums.js`, `dist/shared/index.js` y `dist/server.js` listos para ejecución directa en Node ESM.
2. **Configuración `/tsconfig.json` Autónoma**:
   - Se eliminó `"extends": "../tsconfig.base.json"` y se integraron todas las opciones del compilador (`target: "ES2023"`, `module: "NodeNext"`, `moduleResolution: "NodeNext"`, `rootDir: "src"`, `outDir: "dist"`, `strict: true`, `noImplicitOverride: true`, `noUnusedLocals: true`, `noUnusedParameters: true`, `noFallthroughCasesInSwitch: true`, `forceConsistentCasingInFileNames: true`, `esModuleInterop: true`, `resolveJsonModule: true`, `skipLibCheck: true`, `sourceMap: true`, `declaration: false`, `types: ["node"]`).
3. **Manifiesto `/package.json` Autónomo**:
   - Se eliminó `"@sgemd/shared": "*"` de `dependencies`.
   - Se agregó `"typescript": "7.0.2"` a `devDependencies`.
   - Se incorporó el script `"check:schema": "node scripts/check-schema.mjs"`.

---

## 3. Ajustes de Rutas Tras la Promoción a la Raíz (`/`)

| Archivo | Ruta en Monorepo | Ruta Standalone en Rama `backend` |
|---|---|---|
| `src/config/env.ts` | `existsSync('.env') ? '.env' : '../.env'` | `loadEnv({ path: '.env' })` |
| `scripts/check-schema.mjs` | `resolve(root, 'shared/src/enums.ts')` | `resolve(root, 'src/shared/enums.ts')` |
| `tests/globalSetup.ts` | `const root = resolve(process.cwd(), '..')` | `const root = process.cwd()` (`./database/schema.sql` y `./database/seed.sql`) |
| `tests/env.ts` | `resolve(process.cwd(), '..', 'storage' \| 'backups')` | `resolve(process.cwd(), 'storage' \| 'backups')` |
| `Dockerfile` | Copiaba `shared/` y `backend/` desde el monorepo y ejecutaba `node backend/dist/server.js` | Construye desde `/` (`COPY package.json package-lock.json ./`, `COPY src ./src`) y ejecuta `CMD ["node", "dist/server.js"]` conservando `postgresql17-client`, `rsync` y `tzdata` (`America/Bogota`) |

---

## 4. Directorios y Archivos Podados en la Rama `backend`

- **Cliente Web (SPA)**: `frontend/`
- **Workspace Compartido Antiguo**: `shared/`, `tsconfig.base.json`
- **Infraestructura Monorepo y Proxy**: `caddy/`, `docker-compose.yml`, `docker-compose.dev.yml`, `Makefile`
- **Prototipos HTML y Scaffolds Legados**: `prototype/`, `Config-admin/`, `.stitch/`, `core/`, `agents/`, `skills/`, `interfaces/`, `config/`, `tools/`, `evaluations/`, `crear_estructura_framework.py`
- **Documentos Exclusivos de UI/Frontend**: `docs/design-parity.md`, `CAMBIOS_v1.3.md`, `CORRECCIONES-VISTAS-ESTUDIANTE.md`, `PROTOTIPO-STITCH.md`, `MASTER_IMPLEMENTATION_PROMPT.md`

---

## 5. Comandos Verificados

| Comando | Código de Salida | Resultado |
|---|---|---|
| `npm install` | `0` | Lockfile standalone generado sin dependencias de workspace padre |
| `npm run typecheck` | `0` | `tsc -p tsconfig.json --noEmit` limpio en los 20 módulos y servicios |
| `npm run build` | `0` | Compilación limpia en `dist/` (`dist/server.js`, `dist/shared/enums.js`, etc.) |
| `npm run check:schema` | `0` | 27 clases de negocio, 14 catálogos, 41 tablas y 22 listas `CHECK` verificadas contra `src/shared/enums.ts` |

---

## 6. Lista de Preparación para Despliegue con Supabase (Next-Step Readiness Checklist)

- [x] `database/schema.sql` (41 tablas, 22 restricciones `CHECK`, extensión `btree_gist`) y `database/seed.sql` (14 catálogos, 22 preguntas de diagnóstico, 18 parámetros) disponibles en la raíz `./database/`.
- [x] `npm run check:schema` valida paridad 1:1 entre `database/schema.sql` y `src/shared/enums.ts`.
- [x] `Dockerfile` standalone compila desde la raíz `/` y emite `dist/server.js`.
- [ ] En la fase de despliegue con Supabase: ejecutar `database/schema.sql` y `database/seed.sql` contra la instancia PostgreSQL de Supabase, configurar `DATABASE_URL` con SSL (`?sslmode=require`) en el entorno del backend y definir `APP_ORIGIN` apuntando al dominio de Vercel.
