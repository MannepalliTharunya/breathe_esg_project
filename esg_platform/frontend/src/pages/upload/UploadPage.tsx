import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, RefreshCw, Eye, AlertCircle, CheckCircle, Download } from "lucide-react";
import { useBatches, useUpload, useReprocess } from "../../hooks/useIngestion";
import { BatchStatusBadge, SourceBadge } from "../../components/ui/StatusBadge";
import { Spinner, InlineSpinner } from "../../components/ui/Spinner";
import { PreviewModal } from "./PreviewModal";
import type { UploadBatch } from "../../types";
import { format } from "date-fns";

const SOURCE_TYPES = [
  { value: "sap",     label: "SAP Fuel & Procurement" },
  { value: "utility", label: "Utility Electricity" },
  { value: "travel",  label: "Corporate Travel" },
];

const TEMPLATE_LABELS: Record<string, string> = {
  sap:     "SAP Template",
  utility: "Utility Template",
  travel:  "Travel Template",
};

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function UploadPage() {
  const [sourceType, setSourceType] = useState("sap");
  const [notes, setNotes] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [previewBatch, setPreviewBatch] = useState<string | null>(null);

  const { data, isLoading } = useBatches();
  const upload = useUpload();
  const reprocess = useReprocess();

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"], "application/vnd.ms-excel": [".xls", ".xlsx"] },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024,
  });

  const handleUpload = async () => {
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    fd.append("source_type", sourceType);
    fd.append("notes", notes);
    await upload.mutateAsync(fd);
    setFile(null);
    setNotes("");
  };

  const handleDownloadTemplate = () => {
    // Direct browser download — no auth needed
    const url = `/api/ingestion/template/${sourceType}/`;
    const a = document.createElement("a");
    a.href = url;
    a.download = `${sourceType}_template.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  // Warn if file name looks like wrong source type
  const sourceWarning = (() => {
    if (!file) return null;
    const name = file.name.toLowerCase();
    if (sourceType === "utility" && (name.includes("sap") || name.includes("fuel") || name.includes("travel") || name.includes("employee")))
      return "⚠ File name suggests this may not be a utility/electricity file. Double-check your Data Source selection.";
    if (sourceType === "sap" && (name.includes("employee") || name.includes("travel") || name.includes("kwh") || name.includes("meter")))
      return "⚠ File name suggests this may not be a SAP fuel/procurement file.";
    if (sourceType === "travel" && (name.includes("sap") || name.includes("fuel") || name.includes("kwh") || name.includes("meter")))
      return "⚠ File name suggests this may not be a travel file.";
    return null;
  })();

  const batches = data?.results ?? [];

  return (
    <div>
      <h4 className="fw-bold mb-1">Upload ESG Data</h4>
      <p className="text-muted small mb-4">Upload CSV files from SAP, utility providers, or travel systems.</p>

      <div className="row g-4">
        {/* Upload form */}
        <div className="col-md-5">
          <div className="card">
            <div className="card-header fw-semibold">New Upload</div>
            <div className="card-body">
              {/* Source type */}
              <div className="mb-3">
                <label className="form-label fw-semibold small">Data Source *</label>
                <div className="d-flex flex-column gap-2">
                  {SOURCE_TYPES.map(s => (
                    <div key={s.value} className="form-check">
                      <input className="form-check-input" type="radio" name="source"
                        id={`src-${s.value}`} value={s.value}
                        checked={sourceType === s.value}
                        onChange={() => setSourceType(s.value)} />
                      <label className="form-check-label" htmlFor={`src-${s.value}`}>
                        {s.label}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Drop zone */}
              <div className="mb-3">
                <label className="form-label fw-semibold small">CSV File *</label>
                <div {...getRootProps()} className={`upload-zone ${isDragActive ? "drag-active" : ""}`}>
                  <input {...getInputProps()} />
                  {file ? (
                    <div>
                      <FileText size={32} className="text-success mb-2" />
                      <div className="fw-semibold">{file.name}</div>
                      <div className="text-muted small">{formatBytes(file.size)}</div>
                      <button className="btn btn-link btn-sm text-danger p-0 mt-1"
                        onClick={e => { e.stopPropagation(); setFile(null); }}>
                        Remove
                      </button>
                    </div>
                  ) : (
                    <div>
                      <Upload size={32} className="text-muted mb-2" />
                      <div className="fw-semibold">
                        {isDragActive ? "Drop file here" : "Drag & drop or click to browse"}
                      </div>
                      <div className="text-muted small mt-1">CSV, XLS, XLSX · max 100 MB</div>
                    </div>
                  )}
                </div>
              </div>

              {/* Notes */}
              <div className="mb-3">
                <label className="form-label fw-semibold small">Notes (optional)</label>
                <textarea className="form-control form-control-sm" rows={2}
                  placeholder="e.g. Q1 2024 SAP export from Plant DE01"
                  value={notes} onChange={e => setNotes(e.target.value)} />
              </div>

              {/* Source mismatch warning */}
              {sourceWarning && (
                <div className="alert alert-warning py-2 small mb-3">
                  {sourceWarning}
                </div>
              )}

              <button
                className="btn btn-success w-100"
                onClick={handleUpload}
                disabled={!file || upload.isPending}
              >
                {upload.isPending ? <><InlineSpinner />Processing…</> : <><Upload size={14} className="me-2" />Upload & Process</>}
              </button>

              {upload.isSuccess && (
                <div className="alert alert-success mt-3 py-2 small">
                  <CheckCircle size={14} className="me-1" />
                  File uploaded. Processing started in background.
                </div>
              )}
            </div>
          </div>

          {/* Format hints + template download */}
          <div className="card mt-3">
            <div className="card-header small fw-semibold d-flex align-items-center justify-content-between">
              <span>Expected Columns</span>
              <button
                className="btn btn-outline-success btn-sm d-flex align-items-center gap-1"
                onClick={handleDownloadTemplate}
                title={`Download ${TEMPLATE_LABELS[sourceType]} CSV`}
              >
                <Download size={13} />
                Download Sample Template
              </button>
            </div>
            <div className="card-body small">
              {sourceType === "sap" && (
                <div>
                  <div className="fw-semibold mb-1 text-muted">SAP / German columns supported:</div>
                  <div className="d-flex flex-wrap gap-1 mt-1">
                    {["Plant Code","Material Group","Fuel Type (Material)","Quantity (Menge)","Unit (ME)","Cost Center (Kostenstelle)","Posting Date (Buchungsdatum)","Vendor Name (Lieferant)"].map(c => (
                      <span key={c} className="badge bg-light text-dark border">{c}</span>
                    ))}
                  </div>
                </div>
              )}
              {sourceType === "utility" && (
                <div>
                  <div className="fw-semibold mb-1 text-muted">Utility electricity columns:</div>
                  <div className="d-flex flex-wrap gap-1 mt-1">
                    {["Meter ID","Billing Start Date","Billing End Date","kWh Usage","Tariff Type","Peak Usage","Off Peak Usage","Facility","Supplier"].map(c => (
                      <span key={c} className="badge bg-light text-dark border">{c}</span>
                    ))}
                  </div>
                </div>
              )}
              {sourceType === "travel" && (
                <div>
                  <div className="fw-semibold mb-1 text-muted">Corporate travel columns:</div>
                  <div className="d-flex flex-wrap gap-1 mt-1">
                    {["Employee Name","Travel Type","Departure Airport","Arrival Airport","Distance (km)","Cabin Class","Hotel Nights","Travel Date","Department"].map(c => (
                      <span key={c} className="badge bg-light text-dark border">{c}</span>
                    ))}
                  </div>
                </div>
              )}
              <div className="alert alert-info py-2 mt-3 mb-0 small">
                <strong>Tip:</strong> Click <em>Download Sample Template</em> above to get a ready-to-fill CSV with the correct column names and example data.
              </div>
            </div>
          </div>
        </div>

        {/* Upload history */}
        <div className="col-md-7">
          <div className="card">
            <div className="card-header d-flex align-items-center justify-content-between">
              <span className="fw-semibold">Upload History</span>
              <span className="badge bg-secondary">{data?.count ?? 0} batches</span>
            </div>
            {isLoading ? <Spinner /> : (
              <div className="table-responsive">
                <table className="table table-hover table-sm mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>File</th>
                      <th>Source</th>
                      <th>Status</th>
                      <th className="text-end">Rows</th>
                      <th className="text-end">Failed</th>
                      <th className="text-end">Suspicious</th>
                      <th>Uploaded</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {batches.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="text-center text-muted py-4">No uploads yet</td>
                      </tr>
                    ) : batches.map((b: UploadBatch) => (
                      <tr key={b.id}>
                        <td>
                          <div className="text-truncate" style={{ maxWidth: 180 }} title={b.original_filename}>
                            <FileText size={12} className="me-1 text-muted" />
                            {b.original_filename}
                          </div>
                          {b.error_summary && (
                            <div
                              className="text-danger small mt-1"
                              style={{ maxWidth: 220, cursor: "help" }}
                              title={b.error_summary}
                            >
                              <AlertCircle size={10} className="me-1 flex-shrink-0" />
                              <span className="text-truncate d-inline-block" style={{ maxWidth: 200, verticalAlign: "middle" }}>
                                {b.error_summary}
                              </span>
                            </div>
                          )}
                        </td>
                        <td><SourceBadge source={b.source_type} /></td>
                        <td>
                          <BatchStatusBadge status={b.status} />
                          {(b.status === "processing" || b.status === "pending") && (
                            <span className="spinner-border spinner-border-sm ms-1 text-info" />
                          )}
                        </td>
                        <td className="text-end">{b.total_rows.toLocaleString()}</td>
                        <td className="text-end">
                          <span className={b.failed_rows > 0 ? "text-danger fw-semibold" : "text-muted"}>
                            {b.failed_rows}
                          </span>
                        </td>
                        <td className="text-end">
                          <span className={b.suspicious_rows > 0 ? "text-warning fw-semibold" : "text-muted"}>
                            {b.suspicious_rows}
                          </span>
                        </td>
                        <td className="text-nowrap small text-muted">
                          {format(new Date(b.created_at), "dd MMM HH:mm")}
                        </td>
                        <td>
                          <div className="d-flex gap-1">
                            <button className="btn btn-outline-secondary btn-sm py-0 px-1"
                              title="Preview rows"
                              onClick={() => setPreviewBatch(b.id)}>
                              <Eye size={12} />
                            </button>
                            {b.status === "failed" && (
                              <button className="btn btn-outline-warning btn-sm py-0 px-1"
                                title="Reprocess"
                                disabled={reprocess.isPending}
                                onClick={() => reprocess.mutate(b.id)}>
                                <RefreshCw size={12} />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

      {previewBatch && (
        <PreviewModal batchId={previewBatch} onClose={() => setPreviewBatch(null)} />
      )}
    </div>
  );
}
