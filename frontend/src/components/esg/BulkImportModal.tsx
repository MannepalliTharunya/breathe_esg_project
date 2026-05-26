/**
 * Modal for bulk-importing ESG data from CSV or Excel files.
 */
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileSpreadsheet, X, AlertCircle, CheckCircle } from "lucide-react";
import { useBulkImport, usePeriods, useUploadHistory } from "@/hooks/useESGData";
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

export function BulkImportModal({ onClose }: BulkImportModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [periodId, setPeriodId] = useState("");
  const [result, setResult] = useState<ImportResult | null>(null);
  const { data: periods } = usePeriods();
  const bulkImport = useBulkImport();
  const { data: uploadHistory, isLoading: historyLoading } = useUploadHistory({ page_size: "5" });

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10 MB
  });

  const handleImport = () => {
    if (!file || !periodId) return;
    bulkImport.mutate(
      { file, periodId },
      {
        onSuccess: (data) => setResult(data as ImportResult),
      }
    );
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="import-modal-title"
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 id="import-modal-title" className="font-semibold text-gray-900">Bulk import ESG data</h2>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600 rounded" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          {result ? (
            /* Result view */
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
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Errors</p>
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {result.errors.map((e, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs text-red-700 bg-red-50 rounded p-2">
                        <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" aria-hidden="true" />
                        <span>Row {e.row}: {e.error}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button className="btn-primary w-full" onClick={onClose}>Done</button>
            </div>
          ) : (
            /* Upload form */
            <>
              {/* Template download */}
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
                <strong>Required columns:</strong> metric_code, value, data_source (optional), notes (optional)
              </div>

              {/* Period selector */}
              <div>
                <label htmlFor="import-period" className="label">Reporting period <span className="text-red-500">*</span></label>
                <select
                  id="import-period"
                  className="input"
                  value={periodId}
                  onChange={(e) => setPeriodId(e.target.value)}
                >
                  <option value="">Select a period…</option>
                  {periods?.results.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>

              {/* Dropzone */}
              <div
                {...getRootProps()}
                className={cn(
                  "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors",
                  isDragActive
                    ? "border-brand-400 bg-brand-50"
                    : "border-gray-200 hover:border-brand-300 hover:bg-gray-50"
                )}
              >
                <input {...getInputProps()} aria-label="Upload file" />
                {file ? (
                  <div className="flex items-center justify-center gap-3">
                    <FileSpreadsheet className="w-8 h-8 text-brand-600" aria-hidden="true" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-500">{formatBytes(file.size)}</p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); setFile(null); }}
                      className="ml-2 p-1 text-gray-400 hover:text-red-500"
                      aria-label="Remove file"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <>
                    <Upload className="w-8 h-8 text-gray-300 mx-auto mb-3" aria-hidden="true" />
                    <p className="text-sm font-medium text-gray-700">
                      {isDragActive ? "Drop your file here" : "Drag & drop or click to upload"}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">CSV or Excel · max 10 MB</p>
                  </>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  className="btn-primary flex-1"
                  onClick={handleImport}
                  disabled={!file || !periodId || bulkImport.isPending}
                >
                  {bulkImport.isPending ? "Importing…" : "Import data"}
                </button>
                <button className="btn-secondary" onClick={onClose}>Cancel</button>
              </div>

              {/* Recent Uploads History */}
              <div className="pt-4 border-t border-gray-100 space-y-2">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Recent Uploads</p>
                {historyLoading ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
                  </div>
                ) : !uploadHistory || uploadHistory.results?.length === 0 ? (
                  <p className="text-xs text-gray-400 text-center py-2">No upload records found.</p>
                ) : (
                  <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                    {uploadHistory.results.map((log: any) => (
                      <div key={log.id} className="flex justify-between items-center text-xs p-2 bg-gray-50 rounded hover:bg-gray-100/70 transition-colors">
                        <div className="min-w-0 flex-1 pr-2">
                          <p className="font-medium text-gray-700 truncate">{log.user_email}</p>
                          <p className="text-[10px] text-gray-400">{new Date(log.created_at).toLocaleString()}</p>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-medium flex-shrink-0 ${
                          log.status_code < 400 ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
                        }`}>
                          {log.status_code < 400 ? 'Success' : `Failed (${log.status_code})`}
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
