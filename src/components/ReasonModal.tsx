import { useState, type ReactNode } from 'react';
import { Modal } from './Modal.tsx';
import { TextAreaField } from './FormField.tsx';
import { Button } from './Button.tsx';

interface ReasonModalProps {
  open: boolean;
  title: string;
  label: string;
  hint?: ReactNode;
  confirmLabel?: string;
  required?: boolean;
  loading?: boolean;
  onClose: () => void;
  onSubmit: (reason: string) => void;
}

/**
 * Diálogo con un motivo obligatorio. Se usa para rechazar solicitudes, actas,
 * emprendimientos, devolver tareas y cancelar asesorías: todos esos rechazos
 * exigen texto y el servidor responde `400` sin él.
 */
export function ReasonModal({
  open,
  title,
  label,
  hint,
  confirmLabel = 'Confirmar',
  required = true,
  loading,
  onClose,
  onSubmit,
}: ReasonModalProps) {
  const [reason, setReason] = useState('');

  return (
    <Modal
      open={open}
      title={title}
      onClose={() => {
        setReason('');
        onClose();
      }}
      footer={
        <>
          <Button
            variant="secundario"
            onClick={() => {
              setReason('');
              onClose();
            }}
          >
            Cancelar
          </Button>
          <Button
            variant="primario"
            loading={loading}
            disabled={required && reason.trim().length < 3}
            onClick={() => {
              onSubmit(reason.trim());
              setReason('');
            }}
          >
            {confirmLabel}
          </Button>
        </>
      }
    >
      <TextAreaField
        label={label}
        required={required}
        hint={hint}
        rows={4}
        value={reason}
        onChange={(event) => setReason(event.target.value)}
      />
    </Modal>
  );
}
