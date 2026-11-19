/**
 * Enmascaramiento de datos personales (Ley 1581/2012, T38).
 *
 * El auditor ve las cifras completas pero no los datos que identifican a una persona. El
 * enmascaramiento se hace en el servidor: si se hiciera en la SPA, el dato completo
 * seguiría viajando en la respuesta.
 */

/** `Ana María Restrepo Gómez` → `Ana G.` (primer nombre + inicial del último apellido). */
export function maskName(value: string | null | undefined): string | null {
  if (value === null || value === undefined) return null;
  const parts = value.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return null;
  if (parts.length === 1) return parts[0]!;
  return `${parts[0]} ${parts[parts.length - 1]![0]}.`;
}

/** `900000004` → `******004`: conserva los últimos tres dígitos para conciliar. */
export function maskDocument(value: string | null | undefined): string | null {
  if (!value) return null;
  const clean = value.trim();
  if (clean.length <= 3) return '*'.repeat(clean.length);
  return `${'*'.repeat(clean.length - 3)}${clean.slice(-3)}`;
}

/** `ana.restrepo@uniminuto.edu.co` → `a***@uniminuto.edu.co`. */
export function maskEmail(value: string | null | undefined): string | null {
  if (!value) return null;
  const at = value.indexOf('@');
  if (at <= 0) return '***';
  return `${value[0]}***${value.slice(at)}`;
}
