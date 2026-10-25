import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { env } from '../../config/env.js';

export interface MailMessage {
  to: string;
  subject: string;
  text: string;
  html?: string;
}

export interface Mailer {
  readonly transport: 'file' | 'relay' | 'oauth2';
  send(message: MailMessage): Promise<void>;
}

/**
 * Transporte de desarrollo y pruebas: escribe un `.eml` real en `MAIL_FILE_DIR`.
 *
 * Permite comprobar que el envío ocurrió sin credenciales y sin red. El archivo se crea
 * con permisos 0600: contiene el código OTP.
 */
export class FileMailer implements Mailer {
  readonly transport = 'file' as const;

  constructor(private readonly directory: string) {}

  async send(message: MailMessage): Promise<void> {
    await mkdir(this.directory, { recursive: true, mode: 0o700 });

    const boundary = `sgemd-${randomUUID()}`;
    const headers = [
      `From: ${env.MAIL_FROM}`,
      `To: ${message.to}`,
      `Subject: ${message.subject}`,
      'MIME-Version: 1.0',
      `Date: ${new Date().toUTCString()}`,
      `Content-Type: multipart/alternative; boundary="${boundary}"`,
    ].join('\r\n');

    const parts = [
      `--${boundary}`,
      'Content-Type: text/plain; charset=utf-8',
      'Content-Transfer-Encoding: 8bit',
      '',
      message.text,
    ];

    if (message.html) {
      parts.push(
        `--${boundary}`,
        'Content-Type: text/html; charset=utf-8',
        'Content-Transfer-Encoding: 8bit',
        '',
        message.html,
      );
    }

    parts.push(`--${boundary}--`, '');

    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    const file = join(this.directory, `${stamp}-${randomUUID()}.eml`);
    await writeFile(file, `${headers}\r\n\r\n${parts.join('\r\n')}`, { mode: 0o600 });
  }
}
