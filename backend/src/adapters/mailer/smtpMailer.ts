import nodemailer from 'nodemailer';
import type { Transporter } from 'nodemailer';
import { env } from '../../config/env.js';
import { AppError } from '../../utils/AppError.js';
import type { Mailer, MailMessage } from './fileMailer.js';

/**
 * Transporte real: relay SMTP institucional o Microsoft 365 con OAuth2 (XOAUTH2).
 *
 * Las credenciales las entrega TI (D14). No se inventan valores: si faltan, el arranque
 * falla con un mensaje claro en vez de intentar un envío que nunca funcionaría.
 */
export class SmtpMailer implements Mailer {
  readonly transport: 'relay' | 'oauth2';
  private readonly transporter: Transporter;

  constructor(transport: 'relay' | 'oauth2') {
    this.transport = transport;

    if (!env.MAIL_SMTP_HOST) {
      throw new AppError(500, 'MAIL_NOT_CONFIGURED', 'Falta MAIL_SMTP_HOST para el transporte SMTP');
    }

    if (transport === 'relay') {
      this.transporter = nodemailer.createTransport({
        host: env.MAIL_SMTP_HOST,
        port: env.MAIL_SMTP_PORT,
        secure: env.MAIL_SMTP_PORT === 465,
        auth: env.MAIL_SMTP_USER
          ? { user: env.MAIL_SMTP_USER, pass: env.MAIL_SMTP_PASSWORD ?? '' }
          : undefined,
      });
      return;
    }

    const { MAIL_SMTP_USER, MAIL_OAUTH_CLIENT_ID, MAIL_OAUTH_CLIENT_SECRET, MAIL_OAUTH_REFRESH_TOKEN } =
      env;

    if (!MAIL_SMTP_USER || !MAIL_OAUTH_CLIENT_ID || !MAIL_OAUTH_CLIENT_SECRET || !MAIL_OAUTH_REFRESH_TOKEN) {
      throw new AppError(
        500,
        'MAIL_NOT_CONFIGURED',
        'Faltan credenciales OAuth2 (usuario, client id, client secret y refresh token)',
      );
    }

    this.transporter = nodemailer.createTransport({
      host: env.MAIL_SMTP_HOST,
      port: env.MAIL_SMTP_PORT,
      secure: env.MAIL_SMTP_PORT === 465,
      auth: {
        type: 'OAuth2',
        user: MAIL_SMTP_USER,
        clientId: MAIL_OAUTH_CLIENT_ID,
        clientSecret: MAIL_OAUTH_CLIENT_SECRET,
        refreshToken: MAIL_OAUTH_REFRESH_TOKEN,
      },
    });
  }

  async send(message: MailMessage): Promise<void> {
    await this.transporter.sendMail({
      from: env.MAIL_FROM,
      to: message.to,
      subject: message.subject,
      text: message.text,
      html: message.html,
    });
  }
}
