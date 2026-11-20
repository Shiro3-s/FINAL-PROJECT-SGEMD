# Consolidación de anotaciones del proyecto (organizada)

> **Qué es:** la reorganización de las anotaciones sueltas del equipo, agrupadas por área, sin duplicados, con **estado** y **referencias cruzadas** a lo que ya está documentado.
>
> **Resultado de la revisión:** ✅ **sirve y aporta.** El contenido es **coherente** con la spec (`README.md`), con el flujo real de atención y con los pendientes del estudiante (ambos **material local del área, no versionado**); además **agrega** elementos nuevos (rol de **auditor**, correo de bienvenida, banco de preguntas en **Excel**, rama de **datos** en Git, temas de estudio).
>
> **Fecha:** 2026-10-12.

**Leyenda:** 🆕 = no estaba en la documentación previa · 🔗 = refuerza/duplica algo ya identificado · ⚠️ = decisión o conflicto a resolver · ✅ = ya existe en el prototipo/spec.

---

## 0. Hallazgos de coherencia (revisión rápida)

- ✅ **La validación/candado ya existe en el prototipo:** el `dashboard.html` del estudiante muestra *"Tu cuenta está **Limitada**… el módulo de **Diagnóstico** permanece bloqueado hasta que un administrador active tu cuenta"*. La anotación de §2.2 confirma ese diseño.
- 🔗 **Validación con la asesora** = lo mismo que N1/N2 del doc de pendientes del estudiante.
- 🔗 **Diagnóstico automático** ya es un requisito de negocio del sistema (`docs/fr_nfr_sgemd.md`: **BP-001** "diagnóstico automático de emprendimientos"). §1 lo refuerza.
- ⚠️ **Conflicto de roles:** la spec dice **solo 3 roles** (admin/estudiante/docente); §4.1 pide un **rol de auditor** nuevo → hay que decidir y actualizar la spec.
- ⚠️ **Secciones del formulario:** el prototipo usa **5** secciones (Perfil, Problema, Propuesta de valor, Mercado, Capacidad operativa); la asesora describió **6** secciones distintas. §1.1 propone resolverlo con un **Excel de preguntas** (fuente única). Hay que reconciliar.
- ⚠️ **Documentos de referencia:** de los 3 PDFs citados, **2 existen** como material local del área (**no versionado**, ver §9); **`control.pdf` no está disponible**.

---

## 1. Gestión de diagnóstico

### 1.1 Formulario de diagnóstico
- 🆕 Sacar las preguntas del código y **definirlas en un archivo Excel** (banco de preguntas) como fuente única.
- Integrar ese banco en el módulo **Gestión de diagnóstico**.
- ⚠️ Revisar y **corregir la relación "formulario respondido ↔ diagnóstico autogenerado"**.
- Verificar que el diagnóstico generado **corresponda realmente a las respuestas** del emprendedor.
- ⚠️ La definición actual del diagnóstico **no está bien estructurada** ni relacionada con los demás componentes → redefinirla.

### 1.2 Consulta de resultados
- Al entrar a Gestión de diagnóstico, poder **consultar un resumen** del diagnóstico del emprendedor.
- Generar un **informe descargable** con la caracterización del emprendedor.
- Incorporar **filtros** de consulta y organización.
- Permitir la **descarga** de informes y resultados.

### 1.3 Información adicional
Incorporar, según corresponda al formulario o al perfil:
- **Programa** (académico).
- **Centro educativo** (centro universitario).

---

## 2. Registro y validación del emprendedor

### 2.1 Registro
- Revisar el formulario de registro tomando como referencia **`control.pdf`** ⚠️ (documento no disponible aún).
- Pedir al emprendedor que **complete la información requerida** después de registrarse.
- 🆕 **Automatizar el correo de bienvenida** tras el registro.

### 2.2 Validación administrativa
Validar al emprendedor **antes** de habilitar el acceso completo a la plataforma.

**Flujo propuesto:**
1. **Inscripción** — el emprendedor se registra.
2. **Completar información** — diligencia los datos requeridos.
3. **Notificación** — el sistema notifica a **la coordinadora** (proceso administrativo).
4. **Programación de asesoría** — la coordinadora se comunica para acordar una reunión.
5. **Reunión** — se realiza la asesoría.
6. **Validación** — el administrativo verifica y valida al emprendedor.
7. **Activación** — aprobado → se habilitan las funcionalidades.

> La validación es **condición para desbloquear** el acceso completo. ⚠️ El **alcance exacto del acceso previo** a la aprobación está **pendiente de definir**.

### 2.3 Notificaciones automáticas
Generar notificación al **personal administrativo** cuando el emprendedor:
- Complete su registro y la información requerida.
- Complete el diagnóstico.
- Solicite una asesoría.
- Realice otras acciones relevantes que requieran seguimiento.

### 2.4 Reunión pendiente
- ⚠️ Coordinar reunión con **la coordinadora** para definir y validar: el procedimiento administrativo, los **criterios de aprobación** y **qué funcionalidades se habilitan**.

---

## 3. Caracterización y formulación

Revisar e integrar los documentos de referencia para que formularios y resultados correspondan con los procesos de la plataforma:

- `ficha de carácter y formulación.pdf`
- `Valoración y Diagnóstico.pdf`

**Actividades:**
- Identificar la información solicitada en cada documento.
- Relacionar los campos con los **formularios** y con la **base de datos**.
- Verificar que la caracterización pueda **consultarse y descargarse** en un informe.
- Revisar la relación entre **caracterización, formulación y diagnóstico**.

---

## 4. Gestión de usuarios y roles

### 4.1 Rol de auditor 🆕
- **Crear el rol de auditor.**
- Definir sus **permisos** y funcionalidades.
- Establecer qué información podrá **consultar** y qué acciones podrá **realizar**.
- ⚠️ **Pendiente:** definir el alcance del rol **antes** de implementarlo (y actualizar la spec, que hoy fija solo 3 roles).

### 4.2 Roles administrativos
- Definir los permisos del personal administrativo para **validar** emprendedores.
- Establecer **quién** puede aprobar o rechazar una validación.
- Restringir la **activación de funcionalidades** a los usuarios autorizados.

---

## 5. Base de datos
- Revisar y corregir la **estructura** de la base de datos.
- Verificar las **relaciones** entre usuarios, formularios, caracterizaciones y diagnósticos.
- Comprobar **consistencia** de datos y correspondencia **formularios ↔ tablas**.
- Revisar los campos necesarios para **notificaciones, validación y generación de informes**.

---

## 6. Trabajo colaborativo con Git 🆕
Crear una **rama específica para la inyección y carga de datos**.

**Flujo propuesto:**
1. Crear una rama destinada **exclusivamente** a la inyección de datos.
2. Centralizar allí los cambios de carga/actualización de información.
3. Revisar los cambios antes de integrarlos.
4. Hacer push al repositorio remoto.
5. Integrar en la rama acordada por el equipo.
6. Indicar a los integrantes que actualicen sus repositorios locales.

**Objetivo:** evitar que cada integrante introduzca manualmente la misma información y facilitar la sincronización de datos de prueba.

> ⚠️ **Nota técnica:** si los datos contienen información sensible, **no** deben subirse sin autorización → usar datos ficticios o un mecanismo seguro de distribución (ver la nota de privacidad en `README.md` §16.5).

---

## 7. Temas de estudio y fortalecimiento técnico 🆕

| Área | Temas |
|---|---|
| **Programación** | TypeScript |
| **Seguridad informática** | Ciberseguridad · fundamentos de seguridad de la información |
| **Análisis y diseño** | Diseño de software · conceptos, herramientas y prácticas · seguridad de la información aplicada al desarrollo |

---

## 8. Lista de prioridades

### Prioridad alta — procesos funcionales
- [ ] Definir el flujo de **registro → validación → activación**.
- [ ] **Reunirse con la coordinadora** para acordar el procedimiento administrativo.
- [ ] Corregir la **generación automática del diagnóstico**.
- [ ] Revisar las **relaciones** entre formularios, diagnósticos y base de datos.

### Prioridad media — funcionalidades
- [ ] Implementar el **correo de bienvenida**.
- [ ] Implementar las **notificaciones automáticas**.
- [ ] Crear el **resumen del diagnóstico**.
- [ ] Generar **informes descargables** de caracterización.
- [ ] Agregar **filtros** de consulta.
- [ ] Incorporar los campos de **programa** y **centro educativo**.
- [ ] Definir e implementar el **rol de auditor**.

### Prioridad técnica
- [ ] Crear y documentar la **rama de inyección de datos**.
- [ ] Revisar los cambios de **base de datos**.
- [ ] Verificar **permisos y controles de acceso**.
- [ ] Aprender **TypeScript**.
- [ ] Estudiar **ciberseguridad** y **diseño de software**.

---

## 9. Documentos de referencia

| Documento | Uso previsto | Estado |
|---|---|---|
| `control.pdf` | Referencia para el formulario de registro. | ⚠️ **No está en el repo** |
| `ficha de carácter y formulación.pdf` | Referencia para caracterización y formulación. | ⚠️ Confirmar equivalencia con `CARACATERIZACION EMPRENDIMIENTO CAIMAX.pdf` |
| `Valoración y Diagnóstico.pdf` | Referencia para el diagnóstico y su valoración. | ✅ Disponible como material local del área (**no versionado**) |
| Archivo Excel de preguntas | Fuente para estructurar el formulario de diagnóstico. | ⚠️ **Pendiente** (no es el Excel de proyectos) |

> Nota: los insumos disponibles del área se mantienen como **material local (no versionado)**; no se incluyen en el repositorio por contener datos personales.

---

## 10. Aspectos pendientes por confirmar
- Definición exacta de los **campos obligatorios** del registro.
- **Criterios de validación** del emprendedor.
- **Funcionalidades disponibles antes** de la validación.
- **Permisos** específicos del rol de auditor.
- **Formato y contenido** del informe descargable.
- **Filtros** necesarios en Gestión de diagnóstico.
- **Estructura definitiva** de las tablas y relaciones de la base de datos.
- **Rama de Git** destino de la integración de datos.
- **Alcance** de los temas de análisis y diseño de software a estudiar.

---

## 11. Cómo se conecta con lo ya documentado

| Tema de estas notas | Dónde ya está / se complementa |
|---|---|
| Validación y desbloqueo (§2) | Pendientes del estudiante (material local, no versionado) → **N1/N2** y flujo de atención |
| Diagnóstico / caracterización / valoración (§1, §3) | Insumos y flujo de atención del área (material local, no versionado) → **N3–N5, N9, N10** |
| Acta de confidencialidad | Flujo de atención (material local, no versionado) → **N6** |
| Correcciones del prototipo | `CORRECCIONES-VISTAS-ESTUDIANTE.md` |
| Reglas de negocio y modelo de datos | `README.md` §5–§6 |
