# Orquestación del ajuste al rol docente (2026)

> Documento de trabajo del prototipo **SGEMD**. Resume cómo se orquestó la revisión del
> rol docente/profesor, qué se encontró, qué se corrigió y cómo se verificó. Complementa a
> `cambios-a-docente.md`, que registra el detalle pantalla por pantalla (sección 17).

- **Fecha:** 25 de octubre de 2026
- **Ámbito:** rol docente/profesor
- **Rama de publicación:** `Prototype/Fixsteacher`
- **Estado:** verificado, sin fallos pendientes en el alcance

## 1. Resumen ejecutivo

Se hizo una pasada orquestada sobre las 23 pantallas del rol docente: inventario de textos,
corrección ortográfica, regeneración, verificación estática, segunda red de variantes,
pruebas en navegador y documentación. Se corrigieron **6 hallazgos** (un título, una
etiqueta, una columna de datos, tildes de textos visibles, nombres propios y el changelog
corrupto), se descartó **1 falsa alarma** (paginación) y quedó **1 pendiente fuera de
alcance** en una librería compartida.

| Métrica | Resultado |
|---|---|
| Pantallas docentes regeneradas | 23 |
| Hallazgos corregidos | 6 |
| Falsas alarmas descartadas | 1 |
| Pendientes fuera de alcance | 1 |
| Fallos en la verificación estática | 0 |
| Formas sin tilde sin justificar | 0 |
| Combinaciones responsive revisadas | 20 (4 vistas × 5 anchos) |
| Cambios en `prototype/index.html` | 0 |

## 2. Alcance y restricciones

- Solo el rol **docente/profesor**. No se tocaron `admin/`, `estudiante/`, `compartido/` ni
  las librerías compartidas `lib_ui.py`, `lib_css.py`, `lib_js.py` ni `lib_charts.py`.
- El único generador modificado fue `prototype/paginas_docente.py`; las páginas se
  reconstruyeron con `python generar.py --rol docente`.
- `prototype/index.html` debía quedar **byte-idéntico** y así quedó.
- Se mantuvieron los contratos de URL y filtros: `?f=En+revision`, `?emp=<slug>`,
  `?vista=tabla`, `data-valores="En revision|Devuelta"`.
- Nada se publicó en `main`. El trabajo se sube únicamente a la rama
  `Prototype/Fixsteacher`.

## 3. Orquestación por fases

| Fase | Objetivo | Herramienta | Resultado |
|---|---|---|---|
| 0. Reconocimiento | Localizar el generador único y las cadenas visibles | `read` / `grep` sobre `paginas_docente.py` | 3.027 líneas, 23 pantallas |
| 1. Inventario | Contar ocurrencias exactas antes de tocar el archivo | script de conteo + `fix_tildes_docente.py` | 42 reglas verificadas |
| 2. Corrección | Aplicar tildes y textos aprobados | `fix_tildes_docente.py` ejecutado desde disco | 42 reglas aplicadas |
| 3. Regeneración | Reconstruir todas las pantallas docentes | `python generar.py --rol docente` | 23 pantallas |
| 4. Verificación estática | Texto visible, contratos, contadores e IDs | `verificar_docente.py` | 0 fallos |
| 5. Segunda red | Detectar variantes que conviven con y sin tilde | `segunda_red_texto.py` | 0 formas sin justificar |
| 6. Navegador | Filtros, enlaces, responsive y consola | Chrome DevTools | 20 combinaciones OK |
| 7. Documentación | Registrar el ajuste y la orquestación | `cambios-a-docente.md` + este documento | sección 17 |

**Lección operativa.** PowerShell degradaba a `?` los literales no ASCII enviados por
tubería a Python. Por eso los scripts con acentos se escribieron a disco en UTF-8 y se
ejecutaron desde el archivo; así se evitó corromper el generador y el changelog.

## 4. Hallazgos y bugs

### 4.1 Hallazgos corregidos

| ID | Tipo | Hallazgo | Evidencia | Corrección | Estado |
|---|---|---|---|---|---|
| B-01 | Contenido | «Comportamiento entrepreneurial» sobraba el anglicismo | Tarjeta de Diagnóstico, presente en los 6 contextos | Título «Comportamiento» | Corregido |
| B-02 | Contenido | «Puntaje heuristics» | Tarjeta de Diagnóstico y del expediente | «Puntaje heurístico» | Corregido |
| B-03 | Datos/UI | La columna Fecha repetía «Pendiente» | Krea Textil, EcoPack y Aromas del Sur | «Sin fecha» | Corregido |
| B-04 | Ortografía | Textos visibles sin tilde | 23 pantallas | 42 reglas de reemplazo (`En revisión`, `Última revisión`, `Descripción del avance`, `Calificación`, `Código`, `Observación`, `Cotización`, `Diagnóstico`, `Catálogo`, `Colección`, `Medición`, `Duración`, `Sesión`, `Asesoría`, `Acción`, `Próximas asesorías`, `Acciones rápidas`, `Marcar todo como leído`, `30 días después`, etc.) | Corregido |
| B-05 | Ortografía | Nombres propios sin tilde | Tablas, fichas y previews | **Lucía Fernández**, **Sofía Ramírez**, **Mariana López**, **Andrés Felipe** (64 ocurrencias) | Corregido |
| B-06 | Documentación | El changelog tenía tildes convertidas en `?` | Secciones 15–16: 110 marcas dentro de palabras en 69 líneas | Reparación completa + sección 17 | Corregido |

**Detalle de B-06.** El archivo tenía 152 interrogaciones, de las cuales 110 estaban dentro
de palabras (`a?adi?`, `p?gina`, `Diagn?stico`, `atenci?n`). Tras la reparación quedaron 20,
todas en query strings (`?f=`, `?emp=`, `?vista=`), con comillas «» balanceadas, 638 líneas
y saltos CRLF.

### 4.2 Falsa alarma descartada

| ID | síntoma | diagnóstico | Acción |
|---|---|---|---|
| N-01 | `tareas.html?f=En+revision` mostraba «6 resultados» pero solo 5 filas visibles | La tabla pagina de 5 en 5: la sexta fila está en la página 2 | Sin cambios; no es un bug |

### 4.3 Fuera de alcance

| ID | Hallazgo | Motivo para no tocarlo | Estado |
|---|---|---|---|
| R-01 | Enlace a `evento-form.html` en `lib_js.py:647` | Vive en una librería compartida y las acciones que lo disparan (`aprobar-evento` / `rechazar-evento`) no existen en el rol docente, así que es inalcanzable aquí | Pendiente, documentado |

## 5. Decisiones de diseño

| Decisión | Motivo | Implementación |
|---|---|---|
| Mantener `En revision` como valor interno | No romper enlaces ni filtros existentes | `ESTADO_VIS`, `_estado_vis()` y `_filtro(..., etiquetas=...)` |
| Mostrar «En revisión» en insignias y opciones | Corrección ortográfica sin alterar el dato | El `value` de la opción queda intacto; solo cambia el texto visible |
| No acentuar slugs ni nombres de archivo | URLs y descargas estables | `capacitacion-modelado`, `ficha-tecnica.docx` |
| No tocar identificadores JS ni atributos `data-*` | El motor compara valores y el JS usa `data-accion` | Se editaron solo cadenas visibles |
| Acentuar nombres propios | Aprobado por el usuario | Lucía, Sofía, Mariana y Andrés |

El motor de filtros usa `norm()`, que elimina diacríticos antes de comparar. Por eso una
celda visible «En revisión» sigue coincidiendo con el valor `En revision` y con la opción
`?f=En+revision`.

## 6. Archivos modificados

| Archivo | Cambio |
|---|---|
| `prototype/paginas_docente.py` | Generador único: título, textos, nombres, `ESTADO_VIS`, `_estado_vis()` y `_filtro(..., etiquetas=...)` |
| `prototype/docente/*.html` (23 archivos) | Páginas regeneradas con los textos corregidos |
| `prototype/cambios-a-docente.md` | Sección 17 nueva y reparación de las secciones 15–16 |
| `prototype/orquestacion-docente-2026.md` | Este documento |
| `prototype/index.html` | Sin cambios; no forma parte del commit |

## 7. Verificación reproducible

### 7.1 Comandos

```powershell
cd C:\Users\storm\Videos\profesor\prototype
python -m py_compile paginas_docente.py
python generar.py --rol docente
git diff --exit-code -- index.html
python "$env:TEMP\opencode\verificar_docente.py"
python "$env:TEMP\opencode\segunda_red_texto.py"
```

### 7.2 Resultados estáticos

- `py_compile`: sin errores.
- `generar.py --rol docente`: 23 pantallas generadas.
- `git diff --exit-code -- prototype/index.html`: sin cambios.
- `verificar_docente.py`: **0 fallos**. Comprobó 0 palabras prohibidas en texto visible,
  24 enlaces de métrica, 6 rejillas `g-4`, 3 celdas «Sin fecha», 0 IDs duplicados, la
  opción `value="En revision"` con texto «En revisión» y `data-valores="En revision|Devuelta"`.
- `segunda_red_texto.py`: **0 formas sin justificar** y **0 palabras corruptas**. Quedaron
  tres casos revisados y aceptados: `capacitacion` dentro de la URL visible
  `…/capacitacion-modelado`, y los homógrafos gramaticales `como` y `esta`.

### 7.3 Navegador

| Vista | Comprobación | Resultado |
|---|---|---|
| `tareas.html?f=En+revision` | Opción del filtro | Texto «En revisión», `value="En revision"` |
| `tareas.html?f=En+revision` | Contador y paginación | 6 resultados; 5 en la página 1 y 1 en la página 2 |
| `emprendimientos.html?vista=tabla&f=Con+evidencia` | Filas | 3 |
| `emprendimientos.html?vista=tabla&f=Requieren+atención` | Filas y estados | 2; «En revisión» y «Devuelta» |
| `diagnostico.html` | Tarjetas y enlaces | 6 «Comportamiento», 24 enlaces de métrica, 3 «Sin fecha», 0 «Pendiente/Pendiente» |
| `emprendimiento-expediente.html?emp=ecopack` | Etiquetas | «Última revisión», «Descripción del avance», «Calificación», «Código» |

### 7.4 Responsive

Se revisaron Diagnóstico, Emprendimientos, Tareas y Expediente en **1440, 1280, 1024, 768 y
375 px** (20 combinaciones): sin scroll horizontal, sin recortes de las previews dentro del
viewport y consola sin errores ni advertencias.

## 8. Riesgos y pendientes

- **Scripts de auditoría fuera del repo.** `fix_tildes_docente.py`, `verificar_docente.py`,
  `segunda_red_texto.py`, `segunda_red.py` y `reparar_changelog.py` viven en
  `C:\Users\storm\AppData\Local\Temp\opencode`. Si se pierden, la sección 7 describe las
  comprobaciones y sus resultados esperados. Versionarlos en `prototype/herramientas/`
  queda como mejora opcional.
- **R-01.** El enlace muerto a `evento-form.html` sigue en `lib_js.py:647`; corregirlo
  implica tocar una librería compartida y sale del alcance de este ajuste.
- **Contrato `En revision`.** Si en el futuro se cambia el dato interno, hay que actualizar
  a la vez `ESTADO_VIS`, los filtros y los enlaces con `?f=En+revision`.
- **Tuberías de PowerShell.** No volver a enviar literales con tildes por `@'…'@ | python`;
  escribir el script a disco en UTF-8.

## 9. Estado del repositorio

- Rama base: `prototype/admin-refactor-latest` en `bf570ff`.
- Rama nueva: `Prototype/Fixsteacher`.
- Un solo commit con los 25 archivos modificados más este documento (26 en total).
- Push únicamente de `Prototype/Fixsteacher` a
  `https://github.com/Shiro3-s/FINAL-PROJECT-SGEMD`.
- `main` no se toca: permanece en `197f584`.
- `prototype/index.html` no aparece en el commit porque no cambió.

## 10. Referencias

- `prototype/paginas_docente.py` — generador de las 23 pantallas docentes.
- `prototype/cambios-a-docente.md` — bitácora por pantalla; el ajuste actual es la sección 17.
- `%TEMP%\opencode\fix_tildes_docente.py` — 42 reglas de reemplazo.
- `%TEMP%\opencode\verificar_docente.py` — verificación estática.
- `%TEMP%\opencode\segunda_red_texto.py` — segunda red sobre texto visible.
