import {
  useId,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
  type TextareaHTMLAttributes,
} from 'react';
import { Icon } from './Icon.tsx';

interface FieldProps {
  label: string;
  required?: boolean;
  hint?: ReactNode;
  error?: string;
  /** Id del control; si se omite se genera uno. */
  htmlFor?: string;
  children: (id: string, describedBy: string | undefined) => ReactNode;
}

/**
 * Envoltura de campo: etiqueta, obligatoriedad, ayuda y error.
 *
 * El error se anuncia con `aria-describedby` (no solo con color) y el control
 * recibe `aria-invalid` desde cada campo concreto.
 */
export function Field({ label, required, hint, error, htmlFor, children }: FieldProps) {
  const autoId = useId();
  const id = htmlFor ?? autoId;
  const hintId = hint ? `${id}-ayuda` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [errorId, hintId].filter(Boolean).join(' ') || undefined;

  return (
    <div className="campo">
      <label htmlFor={id}>
        {label}
        {required ? (
          <span className="req" aria-hidden="true">
            *
          </span>
        ) : null}
      </label>
      {children(id, describedBy)}
      {error ? (
        <span className="campo-error" id={errorId}>
          {error}
        </span>
      ) : null}
      {hint ? (
        <span className="ayuda" id={hintId}>
          <Icon name="bombilla" size={14} />
          <span>{hint}</span>
        </span>
      ) : null}
    </div>
  );
}

type TextFieldProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> & {
  label: string;
  hint?: ReactNode;
  error?: string;
  id?: string;
};

export function TextField({ label, hint, error, required, id, ...rest }: TextFieldProps) {
  return (
    <Field label={label} required={required} hint={hint} error={error} htmlFor={id}>
      {(fieldId, describedBy) => (
        <input
          {...rest}
          id={fieldId}
          required={required}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
        />
      )}
    </Field>
  );
}

type SelectFieldProps = Omit<SelectHTMLAttributes<HTMLSelectElement>, 'id'> & {
  label: string;
  hint?: ReactNode;
  error?: string;
  id?: string;
  /** Opción inicial vacía («Seleccione…»). */
  placeholder?: string;
  children: ReactNode;
};

export function SelectField({
  label,
  hint,
  error,
  required,
  id,
  placeholder,
  children,
  ...rest
}: SelectFieldProps) {
  return (
    <Field label={label} required={required} hint={hint} error={error} htmlFor={id}>
      {(fieldId, describedBy) => (
        <select
          {...rest}
          id={fieldId}
          required={required}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
        >
          {placeholder ? <option value="">{placeholder}</option> : null}
          {children}
        </select>
      )}
    </Field>
  );
}

type TextAreaFieldProps = Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'id'> & {
  label: string;
  hint?: ReactNode;
  error?: string;
  id?: string;
};

export function TextAreaField({
  label,
  hint,
  error,
  required,
  id,
  ...rest
}: TextAreaFieldProps) {
  return (
    <Field label={label} required={required} hint={hint} error={error} htmlFor={id}>
      {(fieldId, describedBy) => (
        <textarea
          {...rest}
          id={fieldId}
          required={required}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
        />
      )}
    </Field>
  );
}
