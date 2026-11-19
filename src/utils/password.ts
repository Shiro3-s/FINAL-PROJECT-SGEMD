import bcrypt from 'bcryptjs';

/**
 * Coste de bcrypt. El master §15 exige ≥10; el seed usa `gen_salt('bf', 10)`, así que
 * ambos caminos producen hashes `$2a$10$` intercambiables.
 */
const BCRYPT_COST = 10;

export function hashPassword(plain: string): Promise<string> {
  return bcrypt.hash(plain, BCRYPT_COST);
}

export function verifyPassword(plain: string, hash: string): Promise<boolean> {
  return bcrypt.compare(plain, hash);
}
