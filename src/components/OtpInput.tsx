import { useId, useRef } from 'react';

interface OtpInputProps {
  value: string;
  onChange: (value: string) => void;
  /** Etiqueta accesible del grupo; los campos individuales se numeran. */
  label: string;
  length?: number;
  disabled?: boolean;
}

/**
 * Código OTP de 8 dígitos en campos separados.
 *
 * Pegar el código completo lo reparte entre las casillas; Retroceso en una
 * casilla vacía vuelve a la anterior. El valor se mantiene como una sola cadena
 * para que el formulario lo envíe tal cual.
 */
export function OtpInput({
  value,
  onChange,
  label,
  length = 8,
  disabled,
}: OtpInputProps) {
  const groupId = useId();
  const refs = useRef<Array<HTMLInputElement | null>>([]);

  const digits = Array.from({ length }, (_, index) => value[index] ?? '');

  const setDigit = (index: number, digit: string) => {
    const next = digits.slice();
    next[index] = digit;
    onChange(next.join('').trimEnd());
  };

  const focus = (index: number) => {
    refs.current[index]?.focus();
    refs.current[index]?.select();
  };

  return (
    <div className="otp" role="group" aria-labelledby={groupId}>
      <span id={groupId} className="sr-only">
        {label}
      </span>
      {digits.map((digit, index) => (
        <input
          key={index}
          ref={(element) => {
            refs.current[index] = element;
          }}
          type="text"
          inputMode="numeric"
          autoComplete={index === 0 ? 'one-time-code' : 'off'}
          maxLength={1}
          value={digit}
          disabled={disabled}
          aria-label={`Dígito ${index + 1} de ${length}`}
          onChange={(event) => {
            const raw = event.target.value.replace(/\D/g, '');
            if (!raw) {
              setDigit(index, '');
              return;
            }
            setDigit(index, raw[raw.length - 1]);
            if (index < length - 1) focus(index + 1);
          }}
          onKeyDown={(event) => {
            if (event.key === 'Backspace' && !digit && index > 0) {
              event.preventDefault();
              setDigit(index - 1, '');
              focus(index - 1);
            } else if (event.key === 'ArrowLeft' && index > 0) {
              event.preventDefault();
              focus(index - 1);
            } else if (event.key === 'ArrowRight' && index < length - 1) {
              event.preventDefault();
              focus(index + 1);
            }
          }}
          onPaste={(event) => {
            const pasted = event.clipboardData.getData('text').replace(/\D/g, '');
            if (!pasted) return;
            event.preventDefault();
            onChange(pasted.slice(0, length));
            focus(Math.min(pasted.length, length) - 1);
          }}
        />
      ))}
    </div>
  );
}
