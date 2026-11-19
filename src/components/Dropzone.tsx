import { useRef, useState, type DragEvent } from 'react';
import { Icon } from './Icon.tsx';
import { ProgressBar } from './ProgressBar.tsx';

interface DropzoneProps {
  onFile: (file: File) => void;
  accept?: string;
  disabled?: boolean;
  title?: string;
  note?: string;
  /** Progreso 0–100 mientras se sube; `null` cuando no hay subida en curso. */
  progress?: number | null;
  inputId?: string;
}

/**
 * Zona de carga de evidencias (`.drop` del prototipo).
 *
 * El archivo se envía por `apiUpload` en la página; este componente solo valida
 * que haya un archivo y muestra el progreso real del XHR.
 */
export function Dropzone({
  onFile,
  accept,
  disabled,
  title = 'Arrastra el archivo aquí o haz clic para seleccionarlo',
  note = 'Un archivo por vez.',
  progress = null,
  inputId = 'archivo-evidencia',
}: DropzoneProps) {
  const [over, setOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setOver(false);
    if (disabled) return;
    const file = event.dataTransfer.files[0];
    if (file) onFile(file);
  };

  return (
    <div>
      <label
        htmlFor={inputId}
        className={over ? 'drop sobre' : 'drop'}
        onDragOver={(event) => {
          event.preventDefault();
          if (!disabled) setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={handleDrop}
      >
        <Icon name="upload" size={28} />
        <span className="drop-tit">{title}</span>
        <span className="drop-nota">{note}</span>
        <input
          ref={inputRef}
          id={inputId}
          className="sr-only"
          type="file"
          accept={accept}
          disabled={disabled}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) onFile(file);
            // Permite volver a elegir el mismo archivo tras un error.
            event.target.value = '';
          }}
        />
      </label>
      {progress !== null ? (
        <div style={{ marginTop: 12 }}>
          <ProgressBar value={progress} label="Progreso de la subida" />
          <span className="ayuda" style={{ display: 'block', marginTop: 6 }}>
            Subiendo… {progress}%
          </span>
        </div>
      ) : null}
    </div>
  );
}
