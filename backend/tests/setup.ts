/**
 * Variables de entorno para las pruebas. Valores ficticios, nunca secretos reales.
 * Se cargan antes de importar cualquier módulo que lea `env.ts`.
 */
process.env.NODE_ENV = 'test';
process.env.APP_ORIGIN = 'https://localhost';
process.env.DATABASE_URL = 'postgres://sgemd:test@127.0.0.1:5432/sgemd_test';
process.env.JWT_SECRET = 'test-jwt-secret-de-al-menos-32-caracteres';
process.env.OTP_HMAC_SECRET = 'test-otp-secret-de-al-menos-32-caracteres';
process.env.MAIL_TRANSPORT = 'file';
process.env.COOKIE_SECURE = 'true';
