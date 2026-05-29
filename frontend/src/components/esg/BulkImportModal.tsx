/**
 * Modal for bulk-importing ESG data from CSV or Excel files.
 */
import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileSpreadsheet, X, AlertCircle, CheckCircle, Download } from "lucide-react";
import { useBulkImport, usePeriods } from "@/hooks/useESGData";
import { useDataUploads } from "@/hooks/useMasterData";
import { masterDataService } from "@/services/api/masterData.service";
import { useOrganizationStore } from "@/store/organizationStore";
import { getApiErrorMessage } from "@/utils/apiError";
import { previewImportFile } from "@/utils/csvImportPreview";
import { cn } from "@/utils/cn";
import { formatBytes } from "@/utils/formatters";

interface BulkImportModalProps {
  onClose: () => void;
}

interface ImportResult {
  created: number;
  updated: number;
  errors: Array<{ row: number; error: string }>;
}

interface PreviewRow {
  row: number;
  metric_code: string;
  value: unknown;
  facility_code?: string;
  data_source?: string;
}

const SOURCE_TYPES = [
  { value: "sap", label: "SAP (ERP)" },
  { value: "utility", label: "Utility Portal" },
  { value: "travel", label: "Travel (Concur/Navan)" },
];

export function BulkImportModal({ onClose }: BulkImportModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [periodId, setPeriodId] = useState("");
  const [sourceType, setSourceType] = useState("sap");
  const [result, setResult] = useState<ImportResult | null>(null);
  const [preview, setPreview] = useState<PreviewRow[] | null>(null);
  const [previewErrors, setPreviewErrors] = useState<Array<{ row: number; error: string }>>([]);
  const [previewLoading, setPreviewLoading] = useState(false);

  const { activeOrganization, activeOrganizationId } = useOrganizationStore();
  const { data: periods, isLoading: periodsLoading, isError: periodsError, error: periodsLoadError } = usePeriods();
  const bulkImport = useBulkImport();
  const { data: uploadHistory, isLoading: historyLoading } = useDataUploads({ page_size: "5" });

  const periodList = periods?.results ?? [];

  useEffect(() => {
    if (periodList.length === 0) {
      setPeriodId("");
      return;
    }
    if (!periodList.some((p) => p.id === periodId)) {
      setPeriodId(periodList[0].id);
    }
  }, [periodList, periodId]);

  const onDrop = useCallback(async (accepted: File[]) => {
    const f = accepted[0];
    if (!f) return;
    setFile(f);
    setPreview(null);
    setPreviewErrors([]);
    setPreviewLoading(true);
    try {
      const data = await masterDataService.previewBulkImport(f);
      setPreview((data.preview ?? []) as unknown as PreviewRow[]);
      setPreviewErrors(data.errors ?? []);
      if (data.errors?.length && data.detected_columns?.length) {
        const base = data.errors[0]?.error ?? "";
        if (!base.includes("Found in file")) {
          setPreviewErrors([{
            row: 0,
            error: `${base} Columns in file: ${data.detected_columns.join(", ")}`,
          }]);
        }
      }
    } catch (apiError) {
      const local = await previewImportFile(f);
      setPreview(local.preview as PreviewRow[]);
      setPreviewErrors(
        local.errors.length
          ? local.errors
          : [{ row: 0, error: getApiErrorMessage(apiError, "Could not parse file for preview") }]
      );
    } finally {
      setPreviewLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const handleDownloadTemplate = async () => {
    const { data } = await masterDataService.downloadImportTemplate();
    const url = window.URL.createObjectURL(new Blob([data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = "esg_import_template.csv";
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    if (!file || !periodId) return;
    bulkImport.mutate(
      { file, periodId, sourceType },
      { onSuccess: (data) => setResult(data as ImportResult) }
    );
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="import-modal-title"
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg animate-slide-up max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 sticky top-0 bg-white">
          <h2 id="import-modal-title" className="font-semibold text-gray-900">Bulk import ESG data</h2>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600 rounded" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          {result ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" aria-hidden="true" />
                <div>
                  <p className="font-medium text-green-800">Import complete</p>
                  <p className="text-sm text-green-700 mt-0.5">
                    {result.created} created · {result.updated} updated · {result.errors.length} errors
                  </p>
                </div>
              </div>
              {result.errors.length > 0 && (
                <div className="max-h-40 overflow-y-auto space-y-1">
                  {result.errors.map((e, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-red-700 bg-red-50 rounded p-2">
                      <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                      <span>Row {e.row}: {e.error}</span>
                    </div>
                  ))}
                </div>
              )}
              <button className="btn-primary w-full" onClick={onClose}>Done</button>
            </div>
          ) : (
            <>
              <div className="flex items-start justify-between gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
                <div>
                  <strong>Required columns:</strong> metric_code, value
                  <br />
                  Optional: facility_code, data_source, collection_method, notes
                </div>
                <button
                  type="button"
                  className="btn-secondary text-xs gap-1 flex-shrink-0"
                  onClick={handleDownloadTemplate}
                >
                  <Download className="w-3.5 h-3.5" />
                  Template
                </button>
              </div>

              {!activeOrganizationId && (
                <div className="p-3 text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded-lg" role="alert">
                  No organization selected. Choose an organization from the sidebar, then reopen import.
                </div>
              )}

              {activeOrganization && (
                <p className="text-xs text-gray-500">
                  Organization: <span className="font-medium text-gray-700">{activeOrganization.name}</span>
                </p>
              )}

              {periodsError && (
                <div className="p-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg" role="alert">
                  Could not load reporting periods: {getApiErrorMessage(periodsLoadError)}
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="import-period" className="label">Reporting period <span className="text-red-500">*</span></label>
                  <select
                    id="import-period"
                    className="input"
                    value={periodId}
                    onChange={(e) => setPeriodId(e.target.value)}
                    disabled={periodsLoading || !activeOrganizationId}
                  >
                    <option value="">
                      {periodsLoading
                        ? "Loading periods…"
                        : periodList.length === 0
                          ? "No periods — run seed or select another org"
                          : "Select a period…"}
                    </option>
                    {periodList.map((p) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="source-type" className="label">Source type</label>
                  <select
                    id="source-type"
                    className="input"
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                  >
                    {SOURCE_TYPES.map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div
                {...getRootProps()}
                className={cn(
                  "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors",
                  isDragActive ? "border-brand-400 bg-brand-50" : "border-gray-200 hover:border-brand-300 hover:bg-gray-50"
                )}
              >
                <input {...getInputProps()} aria-label="Upload file" />
                {file ? (
                  <div className="flex items-center justify-center gap-3">
                    <FileSpreadsheet className="w-8 h-8 text-brand-600" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-500">{formatBytes(file.size)}</p>
                    </div>
                  </div>
                ) : (
                  <>
                    <Upload className="w-8 h-8 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm font-medium text-gray-700">
                      {isDragActive ? "Drop your file here" : "Drag & drop or click to upload"}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">CSV or Excel · max 10 MB</p>
                  </>
                )}
              </div>

              {previewLoading && (
                <p className="text-sm text-gray-500 text-center">Parsing preview…</p>
              )}

              {previewErrors.length > 0 && (
                <div className="text-xs text-red-700 bg-red-50 border border-red-200 rounded-lg p-3">
                  {previewErrors.map((e, i) => (
                    <p key={i}>{e.row === 0 ? e.error : `Row ${e.row}: ${e.error}`}</p>
                  ))}
                </div>
              )}

              {preview && preview.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Preview (first rows)</p>
                  <div className="overflow-x-auto border border-gray-100 rounded-lg">
                    <table className="w-full text-xs">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-2 py-1 text-left">Row</th>
                          <th className="px-2 py-1 text-left">Metric</th>
                          <th className="px-2 py-1 text-left">Value</th>
                          <th className="px-2 py-1 text-left">Facility</th>
                        </tr>
                      </thead>
                      <tbody>
                        {preview.map((row) => (
                          <tr key={row.row} className="border-t border-gray-50">
                            <td className="px-2 py-1">{row.row}</td>
                            <td className="px-2 py-1">{row.metric_code}</td>
                            <td className="px-2 py-1">
                              {row.value === null || row.value === undefined || row.value === ""
                                ? "—"
                                : String(row.value)}
                            </td>
                            <td className="px-2 py-1">{row.facility_code || "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                <button
                  className="btn-primary flex-1"
                  onClick={handleImport}
                  disabled={
                    !file ||
                    !periodId ||
                    !activeOrganizationId ||
                    bulkImport.isPending ||
                    previewErrors.some((e) => e.row === 0 && e.error.includes("Missing required columns"))
                  }
                >
                  {bulkImport.isPending ? "Importing…" : "Import data"}
                </button>
                <button className="btn-secondary" onClick={onClose}>Cancel</button>
              </div>

              <div className="pt-4 border-t border-gray-100 space-y-2">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Recent uploads</p>
                {historyLoading ? (
                  <div className="flex justify-center py-4">
                    <div className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
                  </div>
                ) : !uploadHistory?.results?.length ? (
                  <p className="text-xs text-gray-400 text-center py-2">No upload records yet.</p>
                ) : (
                  <div className="space-y-1.5 max-h-36 overflow-y-auto">
                    {uploadHistory.results.map((log) => (
                      <div key={log.id} className="flex justify-between items-center text-xs p-2 bg-gray-50 rounded">
                        <div className="min-w-0 flex-1 pr-2">
                          <p className="font-medium text-gray-700 truncate">{log.file_name}</p>
                          <p className="text-[10px] text-gray-400">
                            {log.uploaded_by_email} · {new Date(log.created_at).toLocaleString()}
                          </p>
                        </div>
                        <span className={cn(
                          "px-2 py-0.5 rounded text-[10px] font-medium flex-shrink-0 border",
                          log.status === "success" && "bg-green-50 text-green-700 border-green-200",
                          log.status === "partial" && "bg-yellow-50 text-yellow-700 border-yellow-200",
                          log.status === "failed" && "bg-red-50 text-red-700 border-red-200",
                        )}>
                          {log.status}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
