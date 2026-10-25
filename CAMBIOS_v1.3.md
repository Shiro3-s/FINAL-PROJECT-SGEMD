# Cambios de la versión 1.3 (solución de respaldos y retención)

Base: v1.2. Solo toca la discrepancia #17 y el riesgo de crecimiento del disco de respaldos. Nuevo ID: **D22**.

## A. Respaldos (riesgo de disco)

| Cambio | Dónde |
|---|---|
| El respaldo de evidencias pasa de "tar completo diario" a **instantánea incremental** (`rsync --link-dest`): cada respaldo es una copia completa y navegable, pero los archivos sin cambios son enlaces duros y no ocupan disco extra | §13.2 `respaldos`, §15 (fila Backups), Stage 10, T24, D13, D22 |
| Orden fijo: primero `pg_dump`, después la instantánea, luego el manifiesto (ruta, tamaño, SHA-256; solo se calculan los archivos nuevos) y la retención | §15, Stage 10 |
| `respaldos` guarda **tamaño lógico** y **tamaño añadido**, para ver la tendencia de crecimiento en el panel | §13.2, Stage 10 |
| Subidas a archivo temporal `*.part` y renombrado al terminar; el respaldo excluye `*.part` y `storage/mail` | §15 (fila Uploads y Backups) |
| `backups/` debe estar en un disco distinto de `storage/`; la imagen del backend incluye `rsync`; `rsync` se ejecuta sin shell | §14, §15, D22 |
| Una instantánea `Fallida` nunca se usa como base de la siguiente | §15, T24 |
| Verificación de integridad bajo demanda: recalcula hashes contra el manifiesto | Stage 10, T24 |
| Simulacro de restauración manual en la Etapa 12 y procedimiento escrito en `database/README.md` (restaurar dump, copiar archivos de la instantánea, reaplicar borrados registrados en la auditoría) | §3.4, Stage 12, §21.1, §22.3 |

## B. Discrepancia #17 (borrado físico vs. respaldos)

Resuelta por **retención documentada**, no por purga:
1. Los respaldos son inmutables; no se reescribe nada.
2. Por los enlaces duros, un archivo borrado desaparece del disco cuando expira la última instantánea que lo contiene: como máximo `backup_retention_days` (30 por defecto) después del borrado.
3. El diálogo de confirmación de BR-006 lo dice, con el valor vigente de la configuración.
4. El texto de tratamiento de datos (checkbox del registro) debe mencionar las copias de respaldo; lo redacta la institución, no este proyecto.
5. Las descargas y exportaciones de respaldos quedan en `auditoria_eventos`.

## C. Queda abierto (no implementado a propósito)

- **Disco separado y copia fuera del servidor**: se exigen en el diseño, pero los entrega TI. Una copia simple de un árbol con enlaces duros lo expande a tamaño completo; hay que preservar los enlaces (por ejemplo `rsync -aH`).
- **Retención por tamaño y alerta de poco espacio**: no están en los requisitos; se proponen a la Coordinadora. El panel solo informa tamaños.
- **¿Hace falta una ventana más corta o purga ante solicitudes de supresión?** Lo decide el propietario junto con protección de datos.

Sin pruebas nuevas: T24 se amplió, el catálogo sigue siendo T01–T40.
