# SGEMD — Backend Standalone & PostgreSQL 17 Schema (`backend` Branch)

> **Rama**: `backend` · **Base**: `feat/mvp-implementation-v1` (`079248a`)  
> **Stack**: Node.js 22 · Express 5.3.0 · TypeScript 7.0.2 · PostgreSQL 17 (`pg`) · Zod 4 · Jose · Vitest 5 + Supertest  
> **Objetivo**: API REST, esquema relacional `database/` y suite de pruebas promovidos a la raíz del repositorio (`/`), listos para despliegue con **Supabase**.

---

## 1. Descripción General

Esta rama contiene **exclusivamente** el servidor backend y la capa de datos del **Sistema de Gestión de Emprendimiento Minuto de Dios (SGEMD)** promovidos a la raíz del repositorio (`/`):

- **20 módulos de dominio Express 5** (`auth`, `users`, `catalogs`, `entrepreneurship`, `acta`, `diagnosis`, `assignments`, `tracing`, `tasks`, `advice`, `events`, `requests`, `notifications`, `reports`, `audit`, `settings`, `backups`, `attachments`, `dashboard`, `health`).
- **41 tablas en PostgreSQL 17** (27 clases de negocio + 14 catálogos) y **22 restricciones `CHECK`** sincronizadas con `src/shared/enums.ts`.
- **21 suites de pruebas de integración y unidad** (`tests/*.test.ts`, 285 casos de prueba).
- **Cero dependencias externas de monorepo**: las enumeraciones canónicas (`src/shared/enums.ts`) se compilan directamente dentro de `dist/shared/` como módulos NodeNext ESM estándar.

---

## 2. Estructura del Directorio Raíz (`/`)

```text
/ (raíz de la rama `backend`)
├── src/
│   ├── shared/
│   │   ├── enums.ts                  # Cadenas canónicas §7.2 en español y tuplas de catálogos
│   │   └── index.ts                  # Re-exporta enums.ts (`./enums.js`)
│   ├── adapters/
│   │   └── mailer/                   # fileMailer.ts, smtpMailer.ts, index.ts
│   ├── config/
│   │   ├── env.ts                    # Validación Zod de variables de entorno (`.env`)
│   │   └── logger.ts                 # Logger estructurado Pino
│   ├── db/
│   │   └── pool.ts                   # pg.Pool, query(), withTransaction(), afterCommit()
│   ├── jobs/
│   │   ├── inactivity.job.ts         # Job de inactividad de 90 días (BR-005)
│   │   ├── overdueTasks.job.ts       # Job de notificación de tareas vencidas
│   │   └── scheduler.ts              # Planificador de tareas en segundo plano
│   ├── middleware/                   # accountState, auth, error, originCheck, rateLimit, role, validate
│   ├── modules/                      # 20 módulos de dominio REST (`/api/*`)
│   ├── policy/                       # accountState.ts, accountTransitions.ts, roles.ts
│   ├── services/                     # accountLifecycle, audit, backupFiles, catalogs, codes, email, etc.
│   ├── types/
│   │   └── express.d.ts
│   ├── utils/                        # AppError, asyncHandler, dates, otp, params, password, respond
│   ├── app.ts                        # Fábrica de la aplicación Express 5
│   └── server.ts                     # Servidor HTTP y apagado controlado
├── database/
│   ├── schema.sql                    # 41 tablas PostgreSQL 17 y 22 restricciones CHECK
│   ├── seed.sql                      # 14 catálogos, 22 preguntas de diagnóstico, 18 parámetros y datos demo
│   └── README.md                     # Guía de inicialización, reinicio y restauración de BD
├── scripts/
│   └── check-schema.mjs              # Verifica que database/schema.sql coincida con src/shared/enums.ts
├── tests/                            # 21 suites de integración Vitest + Supertest (285 tests)
├── storage/
│   └── .gitkeep
├── backups/
│   └── .gitkeep
├── docs/
│   ├── BACKEND_BRANCH_MANIFEST.md    # Manifiesto técnico de separación de la rama `backend`
│   ├── api.md                        # Contrato de la API REST implementada
│   ├── decisions.md                  # Registro de decisiones arquitectónicas (ADRs)
│   ├── diagrama-clases.md            # Modelo de dominio de 27 clases y 14 catálogos (usado por check:schema)
│   ├── traceability.md               # Matriz de trazabilidad FR/NFR/BR -> módulo -> test
│   └── verification.md               # Bitácora de verificación del MVP
├── Dockerfile                        # Dockerfile standalone (contexto de build en `/`)
├── docker-compose.test.yml           # Contenedor efímero PostgreSQL 17 para `npm test`
├── vitest.config.ts                  # Configuración standalone de Vitest 5
├── tsconfig.json                     # Configuración standalone de TypeScript 7 (NodeNext)
├── package.json                      # Manifiesto standalone `@sgemd/backend`
├── package-lock.json                 # Lockfile independiente
├── .env.example                      # Plantilla de variables de entorno del backend
├── .gitignore
└── README.md                         # Guía standalone de instalación, BD y pruebas
```

---

## 3. Requisitos, Compilación y Verificación

- **Node.js**: `>= 22.x`
- **PostgreSQL**: `17.x` (o Supabase PostgreSQL)

```bash
# 1. Instalar dependencias en la raíz
npm install

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Verificar tipos con TypeScript 7
npm run typecheck

# 4. Verificar paridad entre database/schema.sql y src/shared/enums.ts
npm run check:schema

# 5. Compilar a JavaScript ESM en dist/
npm run build

# 6. Ejecutar en producción
npm start
```

### Ejecución de la Suite de Integración (`npm test`)

```bash
# Levantar PostgreSQL 17 efímero de pruebas en 127.0.0.1:55432
docker compose -p sgemd-test -f docker-compose.test.yml up -d --wait postgres

# Ejecutar las 21 suites (285 pruebas)
npm test

# Destruir contenedor de pruebas al finalizar
docker compose -p sgemd-test -f docker-compose.test.yml down -v
```

Consulte [`docs/BACKEND_BRANCH_MANIFEST.md`](./docs/BACKEND_BRANCH_MANIFEST.md) para el detalle completo del desacoplamiento y la lista de preparación para **Supabase**.
