import { env } from '../../config/env.js';
import { FileMailer } from './fileMailer.js';
import type { Mailer } from './fileMailer.js';
import { SmtpMailer } from './smtpMailer.js';

export type { Mailer, MailMessage } from './fileMailer.js';

let instance: Mailer | null = null;

/** Adaptador único de correo, elegido por `MAIL_TRANSPORT` (D14). */
export function getMailer(): Mailer {
  if (!instance) {
    instance =
      env.MAIL_TRANSPORT === 'file'
        ? new FileMailer(env.MAIL_FILE_DIR)
        : new SmtpMailer(env.MAIL_TRANSPORT);
  }
  return instance;
}

/** Solo para pruebas: permite sustituir el transporte sin tocar el resto del código. */
export function setMailerForTests(mailer: Mailer | null): void {
  instance = mailer;
}
