import ExcelJS from 'exceljs';
import PDFDocument from 'pdfkit';
import type { ExportFormat, ReportColumn, ReportRow } from './definition.js';

/**
 * Exportadores de reportes (D6: `exceljs` + `pdfkit`, sin navegador headless).
 *
 * Reciben las mismas columnas y filas que devuelve la consulta del reporte: no calculan ni
 * redondean nada. El PDF trunca visualmente las celdas largas (la descripción completa
 * viaja en CSV y XLSX), porque una tabla PDF no es un volcado de datos.
 */

const AZUL_REAL = 'FF004A93';
const AZUL_PROFUNDO = 'FF162644';
const GRIS_CLARO = 'FFF4F6F9';
const TINTA = 'FF162644';

function text(value: unknown): string {
  if (value === null || value === undefined) return '';
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  return String(value);
}

function csvCell(value: unknown): string {
  const raw = text(value);
  if (/[",\r\n]/.test(raw)) return `"${raw.replace(/"/g, '""')}"`;
  return raw;
}

/** CSV con BOM: Excel en Windows abre las tildes correctamente sin importar nada. */
export function toCsv(columns: readonly ReportColumn[], rows: readonly ReportRow[]): Buffer {
  const lines = [
    columns.map((column) => csvCell(column.header)).join(','),
    ...rows.map((row) => columns.map((column) => csvCell(row[column.key])).join(',')),
  ];
  return Buffer.from(`\uFEFF${lines.join('\r\n')}\r\n`, 'utf8');
}

export interface ExportMeta {
  titulo: string;
  descripcion: string;
  filtros: string;
  generadoEn: string;
  actor: string;
}

export async function toXlsx(
  columns: readonly ReportColumn[],
  rows: readonly ReportRow[],
  meta: ExportMeta,
): Promise<Buffer> {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'SGEMD';
  workbook.created = new Date();

  const portada = workbook.addWorksheet('Portada');
  portada.columns = [{ width: 26 }, { width: 80 }];
  portada.addRow(['Reporte', meta.titulo]);
  portada.addRow(['Descripción', meta.descripcion]);
  portada.addRow(['Filtros', meta.filtros]);
  portada.addRow(['Generado', meta.generadoEn]);
  portada.addRow(['Generado por', meta.actor]);
  portada.addRow(['Filas', rows.length]);
  for (let index = 1; index <= 6; index += 1) {
    portada.getRow(index).getCell(1).font = { bold: true, color: { argb: TINTA } };
  }
  portada.getRow(1).font = { bold: true, size: 16, color: { argb: AZUL_REAL } };

  const sheet = workbook.addWorksheet(meta.titulo.slice(0, 31), {
    views: [{ state: 'frozen', ySplit: 1 }],
  });

  sheet.columns = columns.map((column) => ({
    header: column.header,
    key: column.key,
    width: Math.min(60, Math.max(10, column.width + 2)),
  }));

  const header = sheet.getRow(1);
  header.height = 24;
  header.eachCell((cell) => {
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: AZUL_REAL } };
    cell.font = { bold: true, color: { argb: 'FFFFFFFF' }, size: 11 };
    cell.alignment = { vertical: 'middle', horizontal: 'left' };
  });

  rows.forEach((row, index) => {
    const values: Record<string, string | number | null> = {};
    for (const column of columns) {
      const value = row[column.key];
      values[column.key] = typeof value === 'number' ? value : text(value);
    }
    const added = sheet.addRow(values);
    if (index % 2 === 1) {
      added.eachCell((cell) => {
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: GRIS_CLARO } };
      });
    }
  });

  sheet.autoFilter = {
    from: { row: 1, column: 1 },
    to: { row: 1, column: columns.length },
  };

  const buffer = await workbook.xlsx.writeBuffer();
  return Buffer.from(buffer);
}

/** Parte un texto en líneas que caben en `width` con la fuente ya fijada en el documento. */
function wrap(doc: PDFKit.PDFDocument, value: unknown, width: number): string[] {
  const raw = text(value).replace(/\s+/g, ' ').trim();
  if (raw === '') return [''];

  const words = raw.split(' ');
  const lines: string[] = [];
  let current = '';

  for (const word of words) {
    const candidate = current === '' ? word : `${current} ${word}`;
    if (doc.widthOfString(candidate) <= width) {
      current = candidate;
      continue;
    }
    if (current !== '') lines.push(current);
    current = word;
  }
  if (current !== '') lines.push(current);

  return lines.length > 0 ? lines : [''];
}

export function toPdf(
  columns: readonly ReportColumn[],
  rows: readonly ReportRow[],
  meta: ExportMeta,
): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({
      size: 'A4',
      layout: 'landscape',
      margin: 36,
      bufferPages: true,
      info: { Title: meta.titulo, Author: 'SGEMD' },
    });

    const chunks: Buffer[] = [];
    doc.on('data', (chunk: Buffer) => chunks.push(chunk));
    doc.on('end', () => resolve(Buffer.concat(chunks)));
    doc.on('error', reject);

    const left = doc.page.margins.left;
    const top = doc.page.margins.top;
    const usable = doc.page.width - left - doc.page.margins.right;
    const totalWeight = columns.reduce((sum, column) => sum + column.width, 0);
    const widths = columns.map((column) => (column.width / totalWeight) * usable);

    const drawHeader = (): number => {
      doc.fillColor(AZUL_REAL).font('Helvetica-Bold').fontSize(15);
      doc.text(meta.titulo, left, top, { width: usable });
      doc.fillColor(AZUL_PROFUNDO).font('Helvetica').fontSize(8.5);
      doc.text(meta.descripcion, left, doc.y + 2, { width: usable });
      doc.fillColor('#666666').fontSize(8);
      doc.text(`${meta.filtros} · Generado ${meta.generadoEn} por ${meta.actor} · ${rows.length} filas`, left, doc.y + 2, {
        width: usable,
      });
      doc.moveDown(0.6);
      return doc.y;
    };

    const drawTableHeader = (y: number): number => {
      const height = 20;
      doc.rect(left, y, usable, height).fill(AZUL_REAL);
      doc.fillColor('#FFFFFF').font('Helvetica-Bold').fontSize(7.5);
      let x = left;
      columns.forEach((column, index) => {
        doc.text(column.header, x + 3, y + 6, {
          width: widths[index]! - 6,
          height: 10,
          ellipsis: true,
          lineBreak: false,
        });
        x += widths[index]!;
      });
      return y + height;
    };

    let y = drawHeader();
    y = drawTableHeader(y);
    doc.font('Helvetica').fontSize(7);

    const bottom = doc.page.height - doc.page.margins.bottom - 18;

    rows.forEach((row, rowIndex) => {
      const cellLines = columns.map((column, index) =>
        wrap(doc, row[column.key], widths[index]! - 6),
      );
      const height = Math.max(12, Math.max(...cellLines.map((lines) => lines.length)) * 9 + 5);

      if (y + height > bottom) {
        doc.addPage();
        y = drawHeader();
        y = drawTableHeader(y);
        doc.font('Helvetica').fontSize(7);
      }

      if (rowIndex % 2 === 1) {
        doc.rect(left, y, usable, height).fill(GRIS_CLARO);
      }

      doc.fillColor(TINTA);
      let x = left;
      cellLines.forEach((lines, index) => {
        doc.text(lines.join('\n'), x + 3, y + 3, {
          width: widths[index]! - 6,
          height: height - 4,
          ellipsis: true,
        });
        x += widths[index]!;
      });

      y += height;
    });

    if (rows.length === 0) {
      doc.fillColor('#666666').fontSize(10).text('Sin registros para los filtros elegidos.', left, y + 12);
    }

    const range = doc.bufferedPageRange();
    for (let index = 0; index < range.count; index += 1) {
      doc.switchToPage(range.start + index);
      doc
        .fillColor('#666666')
        .font('Helvetica')
        .fontSize(7)
        .text(
          `SGEMD · página ${index + 1} de ${range.count}`,
          left,
          doc.page.height - doc.page.margins.bottom - 10,
          { width: usable, align: 'right' },
        );
    }

    doc.end();
  });
}

export function contentTypeOf(format: ExportFormat): string {
  switch (format) {
    case 'csv':
      return 'text/csv; charset=utf-8';
    case 'xlsx':
      return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
    case 'pdf':
      return 'application/pdf';
  }
}

export function extensionOf(format: ExportFormat): string {
  return format;
}
