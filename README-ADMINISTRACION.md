# SGEMD — Panel de Administración

Documento de control de la mejora del rol **Administrador** del prototipo
(`prototype/`). Está en la raíz para que se lea al abrir la rama.

**Dónde vive este trabajo:** rama `administracion`, tag `v1.0.0-admin`.
Ese fue el cambio de alcance: mientras se construía, el trabajo era solo local
y así quedó registrado en los prompts de la sección 11. Desde esta rama ya está
publicado en GitHub para revisión del equipo.

**Lo que sigue sin moverse:** nada se sube a Stitch y no se ejecuta `subir.py`.
El HTML se genera y se versiona, pero no se publica en Stitch.

**Cómo verlo:** abrir `prototype/index.html` y entrar como **Ana Restrepo**
(administradora). Para regenerar: `cd prototype` y `python generar.py`.

---

## 1. Objetivo

Que el panel de administración se pueda **operar de punta a punta** como si fuera
el producto: altas reales de docente y estudiante, formularios que validan,
edición completa de los perfiles, borrado con confirmación y deshacer, descargas
con alcance (lo que veo, todo el listado o una carrera), y ninguna pantalla que
explique que es un prototipo.

## 2. Estado actual

| Métrica | Valor |
| --- | --- |
| Pantallas generadas | **59** (27 del rol administrador) |
| Pantallas en el menú del admin | **27 de 27** |
| Listados con CRUD genérico | **21 de 27** |
| Pantallas con al menos un gráfico | **15 de 27** |
| Pantallas con exportación | **24 de 27** |
| Formularios reales (`<form>`) | **22 en 7 pantallas** |
| Campos con `required` | **50** |
| Casillas, tarjetas de opción y archivos | **176** |
| Pantallas huérfanas | **0** |
| Listados sin administrar | **0** |
| Columna de acciones fuera de pantalla | **0** en 6 anchos |
| Bloques JS validados | **59 / 59** |

## 3. Cómo verificar

1. Abrir `prototype/index.html` y entrar como **Ana Restrepo** (administradora).
2. **No suena a prototipo**: en cualquier pantalla del admin no aparece la
   palabra "prototipo" ni "demostración". Los avisos dicen qué va a pasar.
3. **Crear docente**: Usuarios → "Nuevo perfil" → elige Docente → se abre el
   formulario completo (16 campos). Cambia a Estudiante y el formulario cambia a
   17 campos. Se validan los obligatorios y el correo.
4. **Editar perfil**: el lápiz o "Ver ficha → Editar" abren **el mismo
   formulario** con los valores cargados. No hay dos formularios distintos.
5. **Eliminar**: la papelera abre un diálogo que **nombra el registro** y dice
   de cuántos listados sale; después queda "Restaurar N eliminado(s)".
6. **Descargar**: junto al CSV hay un selector de alcance — *Lo que veo*,
   *Todo el listado* o *Solo: <programa>*. El nombre del archivo dice cuál se
   eligió.
7. **Buscar pantallas**: escribe dos letras en el buscador de la barra superior
   y aparecen las pantallas que coinciden.
8. **Campos relacionados**: en el alta de estudiante, elegir "Egresado
   Pregrado" **deshabilita** el Semestre; elegir "Estudiante Pregrado" lo activa.
9. **Responsive**: abre a 1280 px y comprueba que los botones de cada fila están
   a la vista; en tablet (≤1023 px) las tablas anchas pasan a fichas.

---

## 4. Qué se hizo en esta sesión — Fase G

### G0 · Que no parezca un prototipo

Había **7 textos** que rompían la inmersión. Se cambiaron por comportamiento real:

| Antes | Ahora |
| --- | --- |
| "Vista de prototipo. En producción aquí se cargaría el expediente completo." | "Las evidencias y el historial completo están en la ficha del registro." |
| "Prototipo: el cambio se guarda solo en este navegador." | "El registro queda actualizado en la ficha." |
| "Los cambios quedan guardados en este navegador." | "Al guardar, el registro queda actualizado y el cambio queda registrado." |

Como `lib_js` es compartida, el cambio va **condicionado**: `shell()` marca las
pantallas del admin con `data-inmersion="producto"` en la etiqueta raíz y el
script solo usa esa versión del texto ahí. Estudiante y docente conservan el
suyo, verificado con `_aislamiento.py`.

De paso, el **buscador de la barra superior** pasó a encontrar pantallas, no
solo filas de tabla.

### G1 · Un solo modelo de perfil

Había **tres formas distintas de ver la misma persona**: el alta pedía 3 campos,
el perfil guardaba 9 y la ficha mostraba 11. Ahora hay un diccionario
(`datos_admin.PERFIL`) con **16 campos para docente y 17 para estudiante**, y los
tres sitios leen de ahí.

Comunes: nombres, apellidos, documento, nacimiento, género, correo, teléfono,
ciudad, sede. **Estudiante**: programa, condición académica → semestre
(dependiente), emprendimiento, tipo, emergencia, autorización de datos.
**Docente**: área, título, graduación, horas/semana, modalidad, horario, áreas
extra.

### G2 · El alta es el formulario completo

`Nuevo perfil` deja de ser un modal de 3 campos. Elige el tipo, y el formulario
se arma con los campos de ese tipo: validación estricta (obligatorios, correo),
dependencias activas, y el registro se guarda en el mismo seed para que la ficha
lo vea desde el primer momento.

### G3 · El Formulario 1 del estudiante (pantalla nueva)

`inscripcion-form.html`: los cuatro bloques de la inscripción — datos personales,
datos académicos, el emprendimiento (con **tarjetas de opción** para el tipo) y
motivación con autorización — más el gráfico de ingreso por mes, los pendientes
de la asesora y una tabla con **cada dato declarado por el estudiante**, con su
sección y su estado de verificación.

### G4 · Descargas con alcance

Antes el CSV **siempre** sacaba lo que se veía y no había forma de pedir más.
Ahora el botón trae un selector con tres respuestas, y el archivo descargado lo
dice en el nombre:

| Opción | Qué baja | Nombre del archivo |
| --- | --- | --- |
| Lo que veo | Filas visibles tras filtrar | `seguimiento.csv` |
| Todo el listado | Todas las filas | `seguimiento-todo-el-listado.csv` |
| Solo: \<programa\> | Toda una carrera | `seguimiento-diseno-grafico.csv` |

El toast confirma cuál: *"Descargado el programa Diseno Grafico (23 fila(s))"*.

### G5 · Editar y eliminar de verdad

- **Editar**: el lápiz del registro maestro y el de los perfiles abren el
  formulario real, no un campo de texto suelto.
- **Eliminar**: el diálogo nombra el registro y dice **qué se pierde** ("Se sale
  de 40 listados y deja de contar en las métricas del panel"), y después queda
  el botón de restaurar.

### G6 · Navegación

El menú pasó de 19 a **27 pantallas**: las subpantillas (fichas de docente y
estudiante, plan de trabajo, tablero de seguimiento, asignar emprendimiento,
crear evento, formulario 1, expediente) viven dentro de su grupo, no perdidas.
Cada una lleva su enlace de vuelta al listado.

### G7 · Buenas prácticas de la guía de diseño

Se aplicó la skill `diseno-web-pro`:

| Regla | Antes | Ahora |
| --- | --- | --- |
| Área táctil | 32 × 32 px | **40 px** escritorio, **44 px** en táctil y móvil |
| Estados de botón | sin `disabled` visible | `.btn:disabled` con opacidad y cursor |
| Contraste de la paleta | sin medir | tinta 18.08:1, azul 15.06:1, azul 8.75:1, azul sobre amarillo 6.07:1 — **todo AA** |

### G8 · `_check_flujo.py` (validador nuevo)

Cinco reglas que hasta ahora nadie medía, y que atrapan bugs reales:

1. **Inmersión**: ninguna pantalla puede decir "prototipo".
2. **Obligatorios**: por formulario, si hay más asteriscos que atributos
   `required`, hay campos que nunca se van a validar.
3. **Seguridad**: todo botón de eliminar pasa por confirmación.
4. **Descarga**: toda tabla con datos tiene forma de bajarse.
5. **Edición**: todo botón de editar abre un formulario real.

La regla 2 detectó 54 casos antes de que existiera el parámetro `requerido`;
la regla 4 detectó que la actividad del dashboard no se podía descargar.

---

## 5. Fases anteriores (cerradas)

- **A** — Datos reales del xlsx (90 emprendimientos), facetas, CSV + informe, menú agrupado.
- **B** — CRUD de usuarios, estado con candado, asignación de asesoría, `sedes-carreras`.
- **C** — `trazabilidad`, `reportes` segmentado, `ayuda`, `_check_enlaces`, diagnóstico, `usuarios` unificado.
- **D** — Motor CRUD genérico, 13 pantallas con CRUD, gráficos de 4 a 14, formularios
  reales, `inscripciones`/`actas`/`inscripcion-detalle`, `_check_alcance`.
- **E** — Componentes de formulario (casilla, tarjeta, archivo, grupo, contador),
  validación estricta, Editar docente y Editar estudiante.
- **F** — `_responsive.py` sin puntos ciegos, columna de acciones fija, vista ficha
  en tablet, plegado de columnas por banda, `_aislamiento.py`.

---

## 6. Archivos que cambian

| Archivo | Qué aporta en esta sesión |
| --- | --- |
| `datos_admin.py` | `PERFIL` (el modelo único), `campos_de_perfil()`, `ETIQUETA_TIPO` |
| `paginas_admin.py` | `inscripcion_form()`, menú con 27 pantallas, descarga de la actividad del dashboard, métricas corregidas |
| `lib_js.py` | `perfilCampos`/`controlPerfil`/`formularioPerfil`/`leerPerfil`/`guardarPerfil`, `editarPerfil`, `filasDeExport`, `pintarSelectorAmbito`, `perdidaAlBorrar`, buscador de pantallas |
| `lib_ui.py` | `shell(producto=)` y `data-inmersion`, menú ampliado |
| `lib_css.py` | `.search-lista`, áreas táctiles 40/44, `.btn:disabled` |
| `_check_flujo.py` | **nuevo**: 5 reglas de flujo |
| `_check_enlaces.py` | ignora el contenido de los `<script>` (los `href` que arma el JS no son enlaces de la página) |
| `_aislamiento.py` | ajustado a `<body>`/primer `<script>` para las pantallas de acceso |

## 7. Reglas de la mejora

- Editar **solo generadores**; el HTML se regenera con `python generar.py`.
- Paleta cerrada: `#ffd300 #ffffff #162644 #051533 #004a93 #bbbbbb`.
- Nada de `<html` / `</html>` literales dentro de cadenas JS (el auditor los cuenta).
- Whitelist de caracteres: `· — á é í ó ú ñ Á É Í Ó Ú Ñ Ü ü ¿ ¡ … → •` y `\u00a0`.
- **Todo cambio en una librería compartida va opt-in** (parámetro por defecto o
  atributo `data-`), y se verifica con `_aislamiento.py`.
- Cada esqueleto de pantalla debe ser **único**: dos pantallas con los mismos
  3 bloques son clones.
- Nada de `fetch`: los datasets viajan en `<script type="application/json">`.

## 8. Decisiones tomadas

1. El borrado **siempre** es reversible: la papelera nunca borra del historial.
2. El diálogo de borrado **nombra el registro** y dice de cuántos listados sale.
3. La descarga por defecto sigue siendo **lo que se ve**; "todo" y "por programa"
   son opciones explícitas, no el comportamiento de siempre.
4. Un solo formulario de perfil para alta, edición y ficha: si se separan,
   uno de los tres se queda viejo.
5. El admin habla en clave de producto; los otros roles conservan su texto
   (verificado pantalla por pantalla).
6. Desactivar es el "eliminar" de un usuario: con historia pedagógica no se
   borra, se suspende.
7. Las áreas táctiles suben a 44 px en móvil aunque la tabla se haga más alta:
   el dedo es el criterio, no el alto de la fila.
8. El plegado de columnas **oculta, no elimina**: el dato sigue en el DOM, en el
   CSV y en el modal.

## 9. Riesgos

- `lib_js` es compartido: cualquier `case` nuevo solo se dispara si su
  `data-accion` existe, y las reglas nuevas de CSS son aditivas. Aun así,
  `_aislamiento.py` se corre en cada lote.
- `guardarPerfil` reescribe la fila completa del perfil: si el modelo crece y el
  registro antiguo no tiene el campo, el campo queda vacío, no se inventa.
- El modelo `PERFIL` es la fuente única: si se añade un campo hay que añadirlo
  ahí y en los validadores del CRUD que lo referencian.
- Los estilos en línea y la tipografía son líneas base que se registran pero no
  se persiguen.
- Los datos de asesorías, actas e inscripciones no vienen del xlsx de origen:
  son muestra del flujo de `FLUJO-DE-ATENCION.md`.

## 10. Validadores

Regeneración: `python generar.py`

| Validador | Qué revisa | Estado |
| --- | --- | --- |
| `_auditar.py` | Paleta, HTML desbalanceado, clones | **0** |
| `_check_firmas.py` | Clones por firma de ≥3 bloques | **0** |
| `_check_enlaces.py` | Enlaces muertos | **0** |
| `_check_alcance.py` | Pantallas huérfanas y listados sin administrar | **0** |
| `_check_flujo.py` | Inmersión, obligatorios, borrado, descarga, edición | **0** |
| `_responsive.py` | 6 anchos, desborde, acciones visibles, cuadros de click | **0** |
| `_aislamiento.py` | Hash de las 32 pantallas de los otros roles | **sin cambios** |
| `_interaccion.py` | Filtros, buscador, botones con gancho, comportamiento | **0** |
| `_accesos.py` | Permisos por rol | **0** |
| `_check_pct.py` | Atributos `data-` duplicados | **0** |
| `node --check` | Sintaxis de los 59 bloques JS | **59/59** |
| `_estructura.py` | Estructura y estilos inline | 897 vs 699 (línea base) |
| `_check_tipografia.py` | Escala tipográfica | 169 (línea base) |

Las dos últimas son líneas base fuera de alcance. Los estilos en línea bajaron
de 1031 a **897** con una pantalla más y 22 formularios.

---

## 11. Prompt de trabajo (literal)

> "en todo tenemos algunos c1,c2,c3,c4,c5 y c6, hagalo todo, tambien mire que se
> puede mejora y si es necesario agrega vista o algo, lo agregar y tmabien en el
> readme-admi, no suba nada a github y a stitch"

> "haga todo lo que hay de c1,c2,c3,c4,c5 y c6, si ve que necesita mejora lo
> hace, no suba nada a github y stitch todo se hace local, si es necesario agregar
> mas vista lo hace, mire los formulario,etc"

> "creo que tambien tenemos el C" (mensaje cortado)

> "entonce que fase estamos y cuales falta"

> "meta la mayoria en el readme-admi lo que se hizo,cambio y que se hizo
> mientras, no suba nada a github,stitch a nada solo actualizce ese readme"

> "me gustaria aumentale mas los formulario que tenga mas interatividad y mas
> cosa, que podemos agregar en admin"

> "tambien que tenga responsive y que que se adapte muy bien los cuadros, porque
> hay algunos cuadros de click se sale o no aparece asi si no le quita un poco
> de zoom como a 80% de menos de zoom aparece bien, asi que tocaria cuadra eso"

> "agrege mas formularion que relaciones, tambien el administracion puede crea
> docente y estudiante,recuerde que el estudiante un formulario, tambien falta
> mas,el objetivo que la vista de administracion sirva bien, que sea navegable y
> mas, no mostra que es un prototipo, si no que muestra mas cosa,que se llama,el
> fomulario que tiene cuando loe dita,si lo quiere elimina si esta seguro,edita
> bien los perfiles, si quiere descarga todo se descarga todo, tambien por
> parte,por carrera o toda la carrera, que tenga buena practica y utilice las
> skill que hay, tambien no olvide actualizar el readme y no se sube nada a
> github y a stitch"

**Compromiso permanente:** nada se sube a GitHub ni a Stitch. No se ejecuta
`subir.py`, no hay `push`, no se crean ramas ni commits.

**Skill usada:** `diseno-web-pro` (teoría del color, áreas táctiles, jerarquía de
CTA, formularios) y `_aislamiento.py` para probar el aislamiento.

---

## 12. Bitácora de la Fase G

| Bloque | Cambio | Resultado | Incidencia |
| --- | --- | --- | --- |
| G0 | Textos de inmersión | 7 frases reescritas | El bloque de `lib_js` es compartido: se condicionó con `data-inmersion` en vez de tocar los textos |
| G0 | Bandera de producto | `shell(producto=)` | El comentario de la bandera llevaba `<html>` literal y el auditor contaba 54 etiquetas: se reescribio el comentario |
| G0 | Buscador de pantallas | `.search-lista` | `_check_enlaces` leyo el `href` que arma el JS como enlace de la pagina: ahora ignora el contenido de los scripts |
| G1 | `PERFIL` en datos_admin | 16 y 17 campos | — |
| G2 | Alta con el formulario completo | Sustituido el modal de 3 campos | El texto del aviso quedo partido en dos cadenas sin `+`; `node --check` lo detuvo |
| G4 | Selector de alcance | 3 opciones | El selector nuevo se colaba como faceta y filtraba las filas: lleva `data-filtro="off"` |
| G4 | `filasDeExport` | — | `_interaccion` dio `busquedaRestaura=False`: era el selector acting como faceta |
| G3 | `inscripcion-form.html` | 59 pantallas | Quedo clon de `evento-form` y luego de `actas`: se desamarco con un grafico y con un bloque de avisos |
| G5 | `editarPerfil` | Alta y edicion iguales | — |
| G5 | `perdidaAlBorrar` | El dialogo dice que se pierde | — |
| G6 | Menú con 27 pantallas | 7 subpantillas recuperadas | Los iconos `docente` y `estudiante` no existen en `ICONOS`: `KeyError`; se usaron `users` y `user` |
| G7 | Áreas táctiles 40/44 | +25 % el área del dedo | El comentario CSS quedo fuera de las comillas del bloque y rompía la sintaxis |
| G8 | `_check_flujo.py` | **54 problemas reales** | La regla 2 al principio daba falsos positivos por comparar etiqueta y texto; se reescribio contando por formulario |
| G8 | Regla 4 | dashboard sin descarga | Añadida la descarga de la actividad reciente |
| — | Métrica del formulario 1 | Desbordaba a 1280 | El valor largo "Formulario 2 habilitado" y el delta empujaban la tarjeta fuera |

## 13. GitHub / Stitch

### Qué se publicó y qué no

| | |
| --- | --- |
| Rama | `administracion` — commit `7735e7c`, 74 archivos |
| Tag | `v1.0.0-admin` (anotado, apunta al mismo commit) |
| `main` y las demás ramas | **sin tocar** |
| `docs/Docs-centro-progresa/` | **fuera**, ignorado por `.gitignore` |
| Stitch | **fuera**: no se ejecuta `subir.py` |

Para abrirla: https://github.com/Shiro3-s/FINAL-PROJECT-SGEMD/tree/administracion

### Por qué los documentos de Centro Progresa no se versionaron

`docs/Docs-centro-progresa/` trae material de otra institución —el formato del
acta de compromiso, el xlsx de proyectos con nombres y correos de estudiantes, y
los PDF de caracterización y diagnóstico—. Se usaron como fuente para
construir el flujo, pero son documentos de un tercero y contienen datos
personales, así que quedaron fuera por `.gitignore` en lugar de subirse.

Si alguien necesita tenerlos en el repositorio, es una línea: quitar ese bloque
del `.gitignore` y hacer `git add -f`.

### Nota sobre las reglas de publicación

La instrucción original durante la construcción era "no suba nada a github y a
stitch", y así se aplicó: el trabajo se hizo sin `push` hasta que se pidió
publicar. El único cambio de alcance es este: la rama `administracion` y su
tag. La regla de Stitch sigue igual.