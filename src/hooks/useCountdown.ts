import { useEffect, useState } from 'react';

/**
 * Cuenta atrás para los reenvíos de código.
 *
 * El backend impone 60 s (`OTP_RESEND_COOLDOWN_SECONDS`); la cuenta atrás es
 * solo una ayuda visual y nunca sustituye al `429 OTP_COOLDOWN` del servidor.
 */
export function useCountdown(initialSeconds = 0) {
  const [seconds, setSeconds] = useState(initialSeconds);

  useEffect(() => {
    if (seconds <= 0) return;
    const timer = window.setInterval(() => {
      setSeconds((current) => Math.max(0, current - 1));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [seconds]);

  return {
    seconds,
    active: seconds > 0,
    start: (value = 60) => setSeconds(value),
    reset: () => setSeconds(0),
  };
}
