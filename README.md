# SGEMD — Frontend Standalone (`frontend` Branch)

> **Rama**: `frontend` · **Base**: `feat/mvp-implementation-v1` (`079248a`)  
> **Stack**: React 19.3.1 · Vite 8.3.5 · TypeScript 7.0.2 · TanStack Query 5 · React Router 7 · `@fontsource/inter`  
> **Objetivo**: SPA desacoplada en la raíz del repositorio (`/`), lista para despliegue directo en **Vercel**.

---

## 1. Descripción General

Esta rama contiene **exclusivamente** la aplicación cliente (SPA) del **Sistema de Gestión de Emprendimiento Minuto de Dios (SGEMD)** promovida a la raíz del repositorio (`/`).

- **64 vistas institucionales** distribuidas en los roles `Estudiante`, `Docente`, `Admin` y autenticación pública (`Login`, `Registro`, `VerificarOtp`, `Recuperar`).
- **Paleta institucional estricta de 6 tokens hexadecimales**: `#ffd300`, `#ffffff`, `#162644`, `#051533`, `#004a93`, `#bbbbbb`.
- **Cero dependencias externas de monorepo**: las enumeraciones canónicas en español (`@sgemd/shared`) se encuentran integradas en `src/shared/enums.ts` y resueltas mediante alias locales en `tsconfig.json` y `vite.config.ts`.

---

## 2. Estructura del Directorio Raíz (`/`)

```text
/ (raíz de la rama `frontend`)
├── public/
│   └── brand/
│       ├── logo-blanco.png           # Logotipo institucional versión clara
│       └── logo-color.png            # Logotipo institucional versión color
├── src/
│   ├── shared/
│   │   ├── enums.ts                  # Cadenas canónicas §7.2 en español y tuplas de catálogos
│   │   └── index.ts                  # Re-exporta enums.ts (destino del alias `@sgemd/shared`)
│   ├── api/
│   │   ├── client.ts                 # Cliente HTTP/XHR/SSE hacia `/api/*`
│   │   └── types.ts                  # Interfaces DTO del cliente
│   ├── components/                   # 26 componentes institucionales reutilizables
│   ├── context/                      # AuthContext.tsx, ToastContext.tsx
│   ├── hooks/                        # Hooks personalizados de React
│   ├── lib/                          # Utilidades de formato (`America/Bogota`) y mapeo de estados
│   ├── pages/
│   │   ├── auth/                     # Login, Registro, VerificarOtp, Recuperar
│   │   ├── estudiante/               # 19 vistas de estudiante + Acta de confidencialidad
│   │   ├── docente/                  # 20 vistas de docente mentor
│   │   ├── admin/                    # 19 vistas de administrador + revisión de Actas
│   │   └── shared/                   # Vistas transversales compartidas por rol
│   ├── queries/                      # Hooks de TanStack Query por módulo de dominio
│   ├── routes/                       # AppRoutes, RequireAuth, RequireRole, RequireActive
│   ├── styles/                       # tokens.css (6 hex), fonts.css (@fontsource/inter), base, layout
│   ├── App.tsx
│   └── main.tsx
├── docs/
│   ├── FRONTEND_BRANCH_MANIFEST.md   # Manifiesto técnico de separación de la rama `frontend`
│   └── design-parity.md              # Matriz de paridad visual de las 64 vistas
├── index.html
├── vite.config.ts                    # Configuración standalone de Vite 8 con alias `@sgemd/shared`
├── tsconfig.json                     # Configuración standalone de TypeScript 7 (sin `../tsconfig.base.json`)
├── package.json                      # Manifiesto standalone `@sgemd/frontend`
├── package-lock.json                 # Lockfile independiente
├── .env.example                      # Plantilla de variables de entorno del frontend
├── .gitignore
└── README.md                         # Guía de instalación, compilación y despliegue en Vercel
```

---

## 3. Requisitos e Instalación Local

- **Node.js**: `>= 22.x`
- **npm**: `>= 10.x`

```bash
# 1. Instalar dependencias en la raíz
npm install

# 2. Copiar variables de entorno opcionales para desarrollo
cp .env.example .env

# 3. Ejecutar verificación estática de tipos (TypeScript 7)
npm run typecheck

# 4. Iniciar servidor de desarrollo (http://localhost:5173)
npm run dev

# 5. Compilar bundle de producción en dist/
npm run build
```

---

## 4. Configuración para Vercel

Al estar promovido a la raíz (`/`), Vercel detecta automáticamente Vite sin necesidad de configurar `Root Directory`:

| Parámetro en Vercel | Valor |
|---|---|
| **Framework Preset** | `Vite` |
| **Root Directory** | `./` (raíz de la rama `frontend`) |
| **Install Command** | `npm ci` (o `npm install`) |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Node.js Version** | `22.x` |

Consulte [`docs/FRONTEND_BRANCH_MANIFEST.md`](./docs/FRONTEND_BRANCH_MANIFEST.md) para el detalle completo de desacoplamiento, archivos eliminados y verificación de compilación.
