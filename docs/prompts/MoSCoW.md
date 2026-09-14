# SGEMD — Complete Project MoSCoW & Prompt Execution Archive

## 1. Executive Summary

This document serves as the complete project execution archive for the Sistema de Gestión de Emprendimiento Minuto de Dios (SGEMD). It defines the complete product vision, prioritizes requirements using the MoSCoW method, delineates the Minimum Viable Product (MVP) from future releases, and provides a comprehensive prompt architecture for AI-assisted development. The project entails a from-scratch rebuild to eliminate legacy technical debt while delivering a robust platform for students, mentors, and administrators.

## 2. Project Context

SGEMD is a web platform designed to manage end-to-end university student entrepreneurship.

* It centralizes information regarding entrepreneurs, their progress, and their assigned mentors.


* It eliminates reliance on informal spreadsheets by aligning data collection with UNIMINUTO's institutional research standards.


* The system utilizes Node.js for the backend and React for the frontend.



## 3. Current State Assessment

* **Current Maturity:** Early implementation / Rebuild.


* **What exists:** Previous legacy codebase with significant technical debt, inconsistent database schemas, and insecure authentication practices.


* **What is broken:** Authorization flaws (students operating out of scope), mock data in dashboards, dead links, and exposed secrets in version control.


* **What should be preserved:** The core business logic, the three primary roles, and the institutional purpose.


* **What should be replaced:** The entire codebase and database must be rebuilt from scratch. Legacy structures, dummy data, and dual authentication layers must not be carried over.



## 4. Sources of Truth

The primary source of truth is the provided context document: `README_SGEMD.md`.

## 5. Project Constraints

* **Architecture:** Must use Node.js, Express, React, and MySQL (v8) orchestrated via Docker.


* **Security:** Passwords must be hashed with bcrypt (salt 10+). Environment variables must strictly manage secrets.


* **Files:** File attachments (up to 500 MB) must be stored locally on the server for the MVP.


* **Database:** Must be initialized via a clean SQL script upon container creation, without migration scripts from the legacy project.



## 6. Requirements Inventory

* **REQ-AUTH-001:** Registration requires an 8-digit OTP sent via email, valid for 5 minutes, verified strictly on the backend.


* **REQ-AUTH-002:** Authentication must use JWT with an 8-hour expiration.


* **REQ-ROLE-001:** The system must enforce three exact roles: Admin (1), Student (2), and Teacher/Mentor (3).


* **REQ-F-001:** Administrators must be able to create users, create entrepreneurships, and assign mentors to students.


* **REQ-F-002:** Mentors must only view entrepreneurships explicitly assigned to them.


* **REQ-F-003:** Mentors must be able to create tasks and tracing notes for their assigned students.


* **REQ-F-004:** Students must be able to complete tasks, request advice, and view their project's progress.


* **REQ-DATA-001:** Dashboards must derive metrics exclusively from real database queries.


* **REQ-UX-001:** The UI must be fully responsive for desktop and mobile devices.


* **REQ-RT-001:** The system must provide real-time notifications for task assignments and confirmed advice sessions.



## 7. Requirements Ambiguities, Conflicts, and Unknowns

* **Unknown (Tracing Model):** The exact schema for the "seguimientos" (tracing) model requires final confirmation.


* **Resolution:** It is assumed to be a mandatory 1:N relationship between Entrepreneurship and Tracing, with a 1:N relationship mapping the Author to the Tracing note.



## 8. Product Vision

To be the definitive, centralized digital ecosystem for UNIMINUTO, seamlessly connecting student entrepreneurs, mentors, and administrators to foster business creation, track programmatic progress, and ensure data-driven institutional support.

## 9. Product Mission

To eliminate administrative fragmentation and informal tracking (e.g., spreadsheets) by providing a unified platform that securely and accurately reflects the real-time status of student entrepreneurship projects.

## 10. Business Objectives

* Standardize the tracking of entrepreneurship projects across UNIMINUTO.


* Provide verifiable data and dashboards for institutional reporting.


* Ensure secure, scalable, and role-restricted access to academic and business data.



## 11. Product Success Criteria

* 100% of active student entrepreneurships are tracked within the system.
* No critical security vulnerabilities (e.g., exposed OTPs or secrets) are found in production.


* Mentors and students report successful end-to-end task and advice management.

## 12. Users and Roles

* **Administrator (Role 1):** Manages users, creates assignments, oversees all entrepreneurships, and views global dashboards.


* **Student (Role 2):** Owns entrepreneurships, completes assigned tasks, requests advice, and tracks personal progress.


* **Teacher/Mentor (Role 3):** Guides assigned students, creates tasks, confirms advice sessions, and records progress notes.



## 13. Role & Permission Model

* **Admin:** Global Read/Write across all entities. Cannot sign tracing notes as a mentor.


* **Teacher:** Read/Write strictly scoped to assigned students/entrepreneurships. Cannot modify the student's core entrepreneurship details.


* **Student:** Read strictly scoped to their own entrepreneurship; Write access limited to completing tasks, requesting advice, and editing specific profile/entrepreneurship fields (e.g., social media, description).



## 14. Complete User Journeys

**MVP Journey 1: Student Onboarding & Assignment**

1. Student registers using institutional email.


2. Backend generates and emails an 8-digit OTP.


3. Student inputs OTP; backend validates and activates the account.


4. Admin creates an entrepreneurship for the student.


5. Admin assigns a Mentor to the Student.



**MVP Journey 2: Mentorship & Tracking**

1. Mentor logs in and views their assigned dashboard.


2. Mentor selects a student's entrepreneurship.


3. Mentor adds a tracing note with a PDF attachment (up to 500MB).


4. Mentor assigns a deadline-driven task to the student.


5. Student receives a real-time notification, logs in, and marks the task as complete.


6. System recalculates task completion percentage automatically.



## 15. Product Capability Map

* **Identity & Security:** JWT Auth, OTP Verification, RBAC Middleware.


* **User Management:** Profile CRUD, Role Assignment.


* **Core Business:** Entrepreneurship CRUD, Mentor Assignments.


* **Mentorship & Tracking:** Tasks, Tracing Notes, Advice Sessions, Event Registration.


* **File Management:** Local 500MB attachment handling.


* **Analytics:** Real-time role-based Dashboards.


* **Communication:** Real-time notifications via WebSockets (Socket.io).



## 16. Complete Product Scope

The complete product encompasses all MVP features plus post-MVP enhancements such as entrepreneurship comparisons, advanced skills evaluation, global push notifications, and internationalization.

## 17. MoSCoW Overview

Priorities are defined to segregate the essential core platform (MVP) from valuable but non-critical future evolution.

## 18. Must Have

* OTP-based email verification (8-digit, 5-minute expiry).


* JWT Authentication and strict RBAC.


* User and Role management.


* Entrepreneurship and Assignment modules.


* Tracing (seguimientos), Tasks (tareas), and Advice (asesorías).


* File attachments up to 500MB.


* Real-time notifications for tasks and advice.


* Role-specific Dashboards fed by real data.


* Clean Docker-based MySQL initialization.



## 19. Should Have

* Entrepreneurship diagnosis module.


* Event creation and manual attendance registration.


* Advanced profile enhancements (avatars).


* Task planning grouped by project stages.



## 20. Could Have

* Entrepreneurship comparison tool.


* Automated push notifications (general).


* Internationalization.



## 21. Won't Have / Out of Scope

* Legacy databases or migration scripts.


* Mock data in production dashboards.


* OTPs exposed in JSON responses.


* Duplicate authentication layers.


* Unused legacy modules (e.g., old skills evaluation).



## 22. MVP Scope

The MVP includes all **Must Have** capabilities (Priority P0) and **Should Have** capabilities (Priority P1). This guarantees a fully functional ecosystem where registration, assignment, tracking, attachments, events, diagnoses, and analytics function securely from day one.

## 23. Release 2 Scope

Release 2 will focus on **Could Have** (Priority P2) capabilities:

* Entrepreneurship comparative analysis.


* General push notification systems.


* Implementation of the pending skills evaluation module.



## 24. Release 3+ / Future Scope

* Cloud migration for file attachments (moving away from local server storage).


* Full platform internationalization.



## 25. Project Roadmap

```
Phase 0: Architecture & Database Design (Docker, MySQL schema)
    ↓
Phase 1: Backend Foundation (Node.js, Express, Auth, OTP)
    ↓
Phase 2: Core API (Users, Entrepreneurships, Assignments)
    ↓
Phase 3: Mentorship API (Tracing, Tasks, Advice, Files, WebSockets)
    ↓
Phase 4: Frontend Foundation (React, Routing, API Client)
    ↓
Phase 5: Frontend Features & Dashboards
    ↓
Phase 6: MVP Testing & Deployment
    ↓
Phase 7: Release 2 (Comparisons, Push Notifications)

```

## 26. MVP vs Complete Product Strategy

The MVP focuses strictly on securing the data lifecycle and operational workflows. While future capabilities like cloud storage and comparison tools belong to the complete product, the MVP architecture (clean DB schema, strict API boundaries) is designed to support them without requiring structural rewrites later.

## 27. Architecture Strategy

* **Backend:** Node.js with Express. Controller-Service-Route pattern.


* **Frontend:** React SPA with React Router. Centralized API client intercepting 401/403 errors.


* **Database:** MySQL v8 connected via `mysql2` connection pool.


* **Security:** Middleware layer validating JWTs and ensuring ownership/role checks before controller execution.


* **Real-time:** Socket.io integrated into the Express server for notifications.



## 28. Data Strategy

* **Initialization:** Clean SQL script mounted directly into the Docker container.


* **Integrity:** Strict Foreign Keys connecting Users to Entrepreneurships, Assignments, and Tasks.


* **Files:** Stored in local `/uploads` directory, ignored by Git. Deleting a task/tracing note triggers physical file deletion.


* **Passwords:** Exclusively stored as bcrypt hashes; never returned in API payloads.



## 29. Security & Privacy Strategy

* **OTP:** Generated on the server, saved to DB with a 5-minute expiration, and sent via SMTP. It must never be echoed back in the API response.


* **JWT:** 8-hour expiration.


* **Env Vars:** Managed strictly via `.env` files which are `.gitignore`d.


* **Data Access:** Endpoints must validate ownership (e.g., Student querying `/entrepreneurship` only receives their own DB rows).



## 30. UX/UI Strategy

* **Responsiveness:** Required across all views.


* **Navigation:** Protected routes (`PrivateRoute`) based on `allowedRoles`. Dynamic sidebars that only render accessible links.


* **Data Visualization:** Use charting libraries (e.g., Recharts) fed strictly by live backend dashboard endpoints.



## 31. Analytics & Reporting Strategy

* Metrics are calculated dynamically via SQL aggregations (e.g., `COUNT`, `AVG` completion rates).


* Segmented endpoints: `/dashboard/admin`, `/dashboard/teacher`, `/dashboard/student`.



## 32. Testing & Quality Strategy

* End-to-end functional testing based on MVP Acceptance Criteria.


* Focus on authorization tests (ensuring students cannot bypass their scope).


* Verify that file deletions cascade to the physical disk.



## 33. Deployment & Operations Strategy

* **Containerization:** `docker-compose.yml` orchestrating Frontend, Backend, and MySQL services.


* **Environment:** `.env.example` provided for safe placeholder definitions.


* **Initialization:** Zero-touch DB provisioning via initial Docker mount.



## 34. Risk Register

* **Risk:** Legacy data migration contamination. **Mitigation:** Start with a 100% clean schema; do not port old scripts.


* **Risk:** Unauthorized data access. **Mitigation:** Implement strict RBAC middleware at the API route level.


* **Risk:** Server disk exhaustion from attachments. **Mitigation:** Enforce 500MB limits; clean up orphaned files; plan for cloud storage post-MVP.



## 35. Assumptions

* Institutional UNIMINUTO emails can receive standard SMTP emails for OTP verification.


* Mentors/Teachers will actively use the system to track students instead of external spreadsheets.



## 36. Open Questions

* Are there specific matrix indicators defined for the "Diagnosis" module, or should the schema use a dynamic JSON/key-value structure for now?



## 37. Architecture & Product Decisions

* **Decision:** Single role field (`Roles_idRoles1`). Replaces the previous disjointed auth systems.


* **Decision:** File storage remains local for the MVP to reduce immediate infrastructure complexity, with a hard requirement to delete files when parent records are deleted.



## 38. MVP Prompt Archive

### PROMPT-SGEMD-DB-001

* **Project Area:** Database
* **MoSCoW Priority:** Must Have
* **Release:** MVP
* **Related Requirements:** REQ-F-001, REQ-DATA-001
* **Objective:** Generate the clean MySQL v8 schema for the SGEMD MVP.
* **Context:** The project requires a complete database rebuild to discard legacy debt. No migration scripts.
* **Inputs:** `README_SGEMD.md` Data Model section.
* **Dependencies:** None.
* **Prompt:**

```text
Review the Data Model section in the provided README_SGEMD.md.
Create a complete, clean `schema.sql` file for MySQL v8. 
Include all catalog tables (roles, tipodocumentos, etc.) and business entities (usuarios, emprendimiento, asignaciones, seguimientos, tareas, asesorias, diagnosticos, eventos, codigosverificacion).
Ensure strict foreign key constraints. 
Include initial seed data for the catalog tables (e.g., Roles: 1=Admin, 2=Estudiante, 3=Docente).
Do not include any dummy data for users or entrepreneurships. 
Ensure case-consistency (snake_case or camelCase) is strictly applied to avoid Linux MySQL issues.
Output the SQL code in a clear block.

```

* **Expected Output:** A comprehensive `schema.sql` script.
* **Acceptance Criteria:** Valid SQL syntax; all 1:N and N:M relationships properly defined; catalog data seeded.
* **Validation:** Run in a MySQL v8 Docker container without errors.
* **Execution Order:** 1
* **Complexity:** Medium

### PROMPT-SGEMD-BACK-001

* **Project Area:** Backend / Authentication
* **MoSCoW Priority:** Must Have
* **Release:** MVP
* **Related Requirements:** REQ-AUTH-001, REQ-AUTH-002
* **Objective:** Implement the secure OTP registration and JWT login flow.
* **Context:** Previous implementation leaked OTPs to the frontend and lacked backend verification.
* **Inputs:** Node.js/Express environment, `schema.sql`.
* **Dependencies:** PROMPT-SGEMD-DB-001
* **Prompt:**

```text
Act as a Senior Node.js Backend Developer.
Implement the Authentication controllers and services for SGEMD based on README_SGEMD.md.
1. `/auth/register`: Accept student data, hash the password (bcrypt salt 10), save user as `Verificado=0`. Generate an 8-digit numeric OTP, save it to `codigosverificacion` (5 min expiry), and simulate sending an email via Nodemailer (SMTP). DO NOT return the OTP in the JSON response.
2. `/auth/verify`: Accept email and OTP. Validate against DB. If valid and not expired, set `Verificado=1` and `Usado=1`.
3. `/auth/login`: Validate email/password. Return a JWT (8-hour expiry) with user ID and Role ID in the payload. Do not return the password hash.
Ensure all database interactions use parameterized queries via `mysql2`.

```

* **Expected Output:** Express routes, controllers, and services for Auth.
* **Acceptance Criteria:** OTP is never exposed in API response; JWT correctly signed; passwords securely hashed.
* **Validation:** API testing via Postman/Curl.
* **Execution Order:** 2
* **Complexity:** High

### PROMPT-SGEMD-BACK-002

* **Project Area:** Backend / Core
* **MoSCoW Priority:** Must Have
* **Release:** MVP
* **Related Requirements:** REQ-F-002, REQ-F-003
* **Objective:** Implement strictly scoped CRUD for Tracing (Seguimientos) and Tasks (Tareas).
* **Context:** Mentors must only manage assigned students.
* **Inputs:** DB connection, Auth Middleware.
* **Dependencies:** PROMPT-SGEMD-BACK-001
* **Prompt:**

```text
Act as a Senior Node.js Backend Developer.
Implement the CRUD endpoints for `tracing` (seguimientos) and `task` (tareas) according to README_SGEMD.md.
Ensure strict authorization:
- Admin (Role 1): Can read/delete all, but cannot create a tracing note as the author.
- Teacher (Role 3): Can read/create/edit/delete only for entrepreneurships assigned to them via the `asignaciones` table. The `req.user.id` must be automatically set as the author.
- Student (Role 2): Can read tracing notes for their own entrepreneurship. Can read and complete tasks assigned to them.
Implement file attachment handling (up to 500MB) using `multer` storing to local `/uploads`. Ensure deleting a task/tracing note deletes the physical file.
Output the routing, controller, and service code.

```

* **Expected Output:** Secure endpoints for tasks and tracing with file handling.
* **Acceptance Criteria:** RBAC is strictly enforced at the database query level; files save and delete properly.
* **Validation:** API testing with different role JWTs.
* **Execution Order:** 3
* **Complexity:** High

### PROMPT-SGEMD-BACK-003

* **Project Area:** Backend / WebSockets
* **MoSCoW Priority:** Must Have
* **Release:** MVP
* **Related Requirements:** REQ-RT-001
* **Objective:** Implement real-time notifications for Tasks and Advice.
* **Context:** Users need immediate feedback without page refreshes when a mentor assigns a task or confirms an advice session.
* **Inputs:** Existing Express server.
* **Dependencies:** PROMPT-SGEMD-BACK-002
* **Prompt:**

```text
Act as a Node.js Developer.
Integrate `socket.io` into the existing SGEMD Express backend to handle real-time notifications.
1. Authenticate WebSocket connections using the existing JWT.
2. Maintain a mapping of connected `userId` to `socket.id`.
3. Provide a service function `sendNotification(userId, type, message)` that the Task and Advice controllers can call.
4. Trigger a notification when a Teacher creates a Task for a Student, and when a Teacher confirms an Advice session.
Output the Socket.io setup, auth middleware for sockets, and the notification service.

```

* **Expected Output:** Socket.io integration and notification service.
* **Acceptance Criteria:** Sockets authenticate via JWT; specific users receive targeted events.
* **Validation:** Connect multiple simulated clients and trigger events.
* **Execution Order:** 4
* **Complexity:** Medium

### PROMPT-SGEMD-FRONT-001

* **Project Area:** Frontend / Architecture
* **MoSCoW Priority:** Must Have
* **Release:** MVP
* **Related Requirements:** REQ-UX-001
* **Objective:** Scaffold the React SPA with Role-based routing.
* **Context:** Prevent unauthorized access to UI views.
* **Inputs:** React, React Router.
* **Dependencies:** PROMPT-SGEMD-BACK-001
* **Prompt:**

```text
Act as a Senior React Developer.
Scaffold the SGEMD React frontend architecture.
1. Implement a centralized Axios API client (`api.js`) that automatically attaches the JWT from localStorage and intercepts 401/403 responses to clear the token and redirect to `/login`.
2. Create a `PrivateRoute` component that accepts an array of `allowedRoles`. It should redirect unauthenticated users to `/login`, and unauthorized roles to a `/unauthorized` view.
3. Setup the basic routing structure for:
   - Public: `/login`, `/register`, `/verify`
   - Admin (Role 1): `/admin/dashboard`, `/admin/users`
   - Student (Role 2): `/student/dashboard`, `/student/tasks`
   - Teacher (Role 3): `/teacher/dashboard`, `/teacher/assignments`
Output the code for `api.js`, `PrivateRoute.jsx`, and `App.jsx`.

```

* **Expected Output:** Axios interceptor, PrivateRoute component, Main router.
* **Acceptance Criteria:** 401s auto-logout; UI blocks users based on role payload in JWT.
* **Validation:** Manual browser testing.
* **Execution Order:** 5
* **Complexity:** Medium

## 39. Post-MVP Prompt Archive

### PROMPT-SGEMD-POST-001

* **Project Area:** Backend / Analytics
* **MoSCoW Priority:** Could Have
* **Release:** Release 2
* **Related Requirements:** Comparativa de emprendimientos
* **Objective:** Build comparison endpoint for entrepreneurships.
* **Context:** Post-MVP requirement to compare progress across different student projects.
* **Inputs:** DB Schema.
* **Dependencies:** MVP fully deployed.
* **Prompt:**

```text
Act as a Node.js Backend Developer.
Create a new endpoint `/entrepreneurship/compare` restricted to Admin and Teachers.
The endpoint should accept an array of `entrepreneurshipIds`.
Query the database to aggregate and return:
1. Current stage of each project.
2. Task completion percentage for each project.
3. Number of tracing notes and advice sessions.
Return the data structured for frontend charting.

```

* **Expected Output:** Comparison controller and service.
* **Acceptance Criteria:** Accurately aggregates data across multiple IDs.
* **Validation:** API unit tests.
* **Execution Order:** Post-MVP
* **Complexity:** Medium

## 40. Future Evolution Prompt Archive

*(Reserved for Cloud Storage Migration Prompts and Internationalization Prompts to be detailed when Phase 3 initiates).*

## 41. Requirement → Capability → Release → Prompt Traceability Matrix

| Requirement | Capability | MoSCoW | Release | Prompt ID |
| --- | --- | --- | --- | --- |
| REQ-DATA-001 | Database Schema | Must | MVP | PROMPT-...-DB-001 |
| REQ-AUTH-001 | Auth API | Must | MVP | PROMPT-...-BACK-001 |
| REQ-F-002 | Scoped CRUD API | Must | MVP | PROMPT-...-BACK-002 |
| REQ-RT-001 | WebSockets | Must | MVP | PROMPT-...-BACK-003 |
| REQ-UX-001 | React Routing | Must | MVP | PROMPT-...-FRONT-001 |

## 42. Prompt Dependency Graph

```
PROMPT-SGEMD-DB-001
        ↓
PROMPT-SGEMD-BACK-001
       / \
      ↓   ↓
BACK-002  FRONT-001
      ↓
BACK-003

```

## 43. Recommended Execution Sequence

1. Database Schema Definition & Docker Setup.
2. Backend Auth & User Role Base.
3. Core Backend CRUD (Entrepreneurships, Assignments).
4. Complex Backend Workflows (Tracing, Tasks, Files, WebSockets).
5. Frontend Foundation (Auth, Routing, API Client).
6. Frontend Views & Dashboards.

## 44. Parallel Workstreams

Once API contracts and the Database Schema (PROMPT-SGEMD-DB-001) are established, Frontend UI component development (Cards, Forms, Layouts) can happen in parallel with Backend endpoint implementation.

## 45. Critical Path

Docker DB Setup → Backend Auth → Assignment Logic → Tracing/Tasks API → Frontend Auth → Frontend Dashboards.

## 46. Release Readiness Criteria

* Zero exposed credentials in the codebase or APIs.
* File uploads and physical deletions work seamlessly on the server.
* Students cannot access mentor endpoints or view other students' data.
* Docker `docker-compose up` launches the entire stack cleanly from scratch.

## 47. MVP Definition of Done

* All P0 (Must Have) and P1 (Should Have) requirements are implemented.
* Code passes end-to-end user journey tests.
* System is deployed to a staging environment mirroring production.
* README updated with deployment instructions.
* No mock data remains; all dashboard data originates from MySQL.

## 48. Complete Product Definition of Done

* Post-MVP features (Comparison, Evaluation, Push Notifications) are fully integrated.
* File storage is successfully migrated to cloud storage (e.g., AWS S3).
* Platform meets all institutional reporting requirements for Centro Progresa.

## 49. Post-MVP Backlog

* Implement the Entrepreneurship Comparison tool.
* Implement advanced skills evaluations.
* Migrate local file uploads to Cloud/S3.
* Add General Push Notifications.

## 50. Final Project Checklist

* [ ] Database Schema validated against legacy conflicts.
* [ ] `.env.example` created and `.env` added to `.gitignore`.
* [ ] OTP logic strictly confined to backend email generation.
* [ ] File deletion cascade logic verified.
* [ ] Frontend API interceptor successfully clears expired tokens.
* [ ] MVP scope clearly isolated from Future scope to prevent feature creep.
