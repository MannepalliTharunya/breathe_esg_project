export interface CsvPreviewRow {
  row: number;
  metric_code: string;
  value: unknown;
  facility_code?: string;
  data_source?: string;
  notes?: string;
}

export interface CsvPreviewResult {
  preview: CsvPreviewRow[];
  row_count: number;
  errors: Array<{ row: number; error: string }>;
  detected_columns?: string[];
}

const COLUMN_ALIASES: Record<string, string[]> = {
  metric_code: ["metric_code", "metric", "metric_name", "esg_metric", "indicator", "kpi"],
  value: ["value", "values", "amount", "numeric_value", "reading", "quantity", "usage", "consumption"],
};

function normalizeHeader(name: string): string {
  return name.trim().toLowerCase().replace(/^\ufeff/, "").replace(/\s+/g, "_");
}

function mapHeaders(headers: string[]): { mapped: string[]; rename: Record<number, string> } {
  const mapped = [...headers];
  const rename: Record<number, string> = {};
  const used = new Set<string>();

  headers.forEach((h, idx) => {
    const n = normalizeHeader(h);
    for (const [canonical, aliases] of Object.entries(COLUMN_ALIASES)) {
      const keys = new Set([canonical, ...aliases.map(normalizeHeader)]);
      if (keys.has(n) && !used.has(canonical)) {
        rename[idx] = canonical;
        mapped[idx] = canonical;
        used.add(canonical);
        break;
      }
    }
  });
  return { mapped, rename };
}

/** Parse CSV text client-side for import preview (no backend required). */
export function parseCsvImportPreview(text: string, limit = 10): CsvPreviewResult {
  const lines = text.trim().split(/\r?\n/).filter((l) => l.trim());
  if (lines.length === 0) {
    return { preview: [], row_count: 0, errors: [{ row: 0, error: "File is empty" }] };
  }

  const rawHeaders = lines[0].split(",").map((h) => h.trim());
  const detected_columns = rawHeaders;
  const { mapped: headers } = mapHeaders(rawHeaders.map(normalizeHeader));

  const missing = ["metric_code", "value"].filter((c) => !headers.includes(c));
  if (missing.length) {
    return {
      preview: [],
      row_count: Math.max(0, lines.length - 1),
      detected_columns,
      errors: [{
        row: 0,
        error: `Missing required columns: ${missing.join(", ")}. Found: ${detected_columns.join(", ")}. Use metric_code & value or download the template.`,
      }],
    };
  }

  const preview: CsvPreviewRow[] = [];
  for (let i = 1; i < lines.length && preview.length < limit; i++) {
    const cols = lines[i].split(",");
    const row: Record<string, string> = {};
    headers.forEach((h, idx) => {
      row[h] = (cols[idx] ?? "").trim();
    });
    preview.push({
      row: i + 1,
      metric_code: row.metric_code ?? "",
      value: row.value ?? "",
      facility_code: row.facility_code,
      data_source: row.data_source,
      notes: row.notes,
    });
  }

  return { preview, row_count: lines.length - 1, errors: [], detected_columns };
}

export async function previewImportFile(file: File): Promise<CsvPreviewResult> {
  if (!file.name.toLowerCase().endsWith(".csv")) {
    return {
      preview: [],
      row_count: 0,
      errors: [{
        row: 0,
        error: "Excel preview uses the server. If columns are wrong, rename to metric_code & value or use the template.",
      }],
    };
  }
  const text = await file.text();
  return parseCsvImportPreview(text);
}
