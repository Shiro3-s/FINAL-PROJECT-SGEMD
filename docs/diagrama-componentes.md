# Diagrama de Componentes — SGEMD

Sistema de Gestión de Emprendimiento Minuto de Dios. Diagrama de componentes
del MVP: frontend React, backend Node/Express, seguridad (JWT + bcrypt + OTP),
persistencia **PostgreSQL**, notificaciones en tiempo real (Socket.io),
almacenamiento de archivos (≤ 500 MB), servicio SMTP e infraestructura Docker.

## Diagrama (Mermaid)

```mermaid
flowchart TB
    subgraph FRONT["Frontend — React (SPA)"]
        direction LR
        F_AUTH["Auth · Login / Registro<br/>(OTP 8 dígitos)"]
        F_ADMIN["Panel Admin<br/>usuarios · emprendimientos · asignaciones"]
        F_DOC["Panel Docente / Mentor<br/>seguimientos · tareas · asesorías"]
        F_EST["Panel Estudiante<br/>progreso · tareas · avance"]
        F_API["Cliente API central<br/>Bearer token · redirige en 401/403"]
    end

    subgraph BACK["Backend — Node.js + Express (API REST /api)"]
        direction TB
        subgraph MW["Middleware"]
            M_AUTH["authenticateToken (JWT)"]
            M_ROL["isAdmin · isTeacher · isStudent"]
        end
        subgraph SVC["Servicios por módulo<br/>routes → controllers → services → BD"]
            S_AUTH["AuthService<br/>register · verify · login · logout"]
            S_USER["UserService<br/>CRUD · avatar · roles"]
            S_EMP["EmprendimientoService<br/>CRUD · etapas · emprendimientos paralelos"]
            S_ASIG["AsignaciónService<br/>mentor ↔ estudiante ↔ emprendimiento"]
            S_SEG["SeguimientoService<br/>notas de acompañamiento"]
            S_TAREA["TareaService<br/>CRUD · completar · % avance"]
            S_ASES["AsesoríaService<br/>solicitud · confirmación · agenda"]
            S_EVENT["EventoService<br/>eventos · registro de asistencia"]
            S_DIAG["DiagnósticoService"]
            S_DASH["DashboardService<br/>métricas reales de BD"]
        end
        VAL["Validación de entrada +<br/>consultas SQL parametrizadas"]
        SOCK["Socket.io<br/>Notificaciones en tiempo real"]
        FIL["File storage<br/>Uploads locales (≤ 500 MB)"]
    end

    subgraph SEG["Seguridad"]
        JWT["JWT · expiración 8 h"]
        BCRYPT["bcrypt · hash de contraseñas"]
        OTP["Código OTP · validez 5 min"]
    end

    subgraph DB["Persistencia — PostgreSQL"]
        direction LR
        T_USU["usuarios<br/>(1=Admin · 2=Estudiante · 3=Docente)"]
        T_EMP["emprendimiento<br/>(etapa · propietario)"]
        T_ASIG["asignaciones<br/>(mentor ↔ estudiante)"]
        T_SEG["seguimientos"]
        T_TAREA["tareas"]
        T_ASES["asesorías"]
        T_EVENT["eventos<br/>+ usuarios_has_Eventos"]
        T_COD["códigos de verificación (OTP)"]
        T_CAT["catálogos<br/>(roles · documento · programa · municipio ·…)"]
    end

    SMTP["Externo — SMTP<br/>envío de correo de verificación"]

    subgraph INFRA["Infraestructura"]
        DOCKER["docker-compose<br/>backend | frontend | postgres"]
        ENV[".env<br/>secretos y credenciales"]
    end

    F_AUTH --> F_API
    F_ADMIN --> F_API
    F_DOC --> F_API
    F_EST --> F_API

    F_API -->|"HTTP/JSON · Authorization: Bearer"| M_AUTH
    M_AUTH --> M_ROL
    M_ROL --> SVC

    S_AUTH --> JWT
    S_AUTH --> BCRYPT
    S_AUTH --> OTP
    S_AUTH --> SMTP
    OTP --> T_COD

    SVC --> VAL
    SVC --> SOCK
    SVC --> FIL
    SOCK -.->|"Notificaciones tiempo real"| F_API
    VAL --> DB

    DB --> DOCKER
    ENV -.-> DOCKER
```

Fuente: `README.md` del proyecto (roles, API, modelo de datos y arquitectura).

## Cómo llevarlo a draw.io (visual)

1. **Opción A — Importar PNG:** abre draw.io y arrastra `diagrama-componentes.png`
   dentro del lienzo, o *File → Insert from… → Image*.
2. **Opción B — Abrir el `.drawio` editable:** abre `diagrama-componentes.drawio`
   en draw.io desktop o en app.diagrams.net y edítalo con formas nativas.
3. **Opción C — Mermaid → draw.io online:** copia el bloque Mermaid de arriba a
   mermaid.live, exporta la imagen y arrástrala a draw.io.

## Archivos generados

| Archivo                       | Formato    | Uso                                       |
| ----------------------------- | ---------- | ----------------------------------------- |
| `diagrama-componentes.md`     | Markdown   | Diagrama en Mermaid (este documento)      |
| `diagrama-componentes.png`    | Imagen     | Vista visual (importable a draw.io)       |
| `diagrama-componentes.drawio` | XML/mxGraph| Editable directamente en draw.io          |