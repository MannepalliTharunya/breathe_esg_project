import { X, AlertTriangle, Lock, CheckCircle, XCircle, Flag, Clock } from "lucide-react";
import { useRecordHistory } from "../../hooks/useReview";
import { RecordStatusBadge, ScopeBadge, SourceBadge } from "../../components/ui/StatusBadge";
import type { NormalizedRecord, ApprovalWorkflow } from "../../types";
import { format } from "date-fns";

interface Props {
  record: NormalizedRecord;
  onClose: () => void;
  onApprove: () => void;
  onReject: () => void;
  onFlag: () => void;
}

export function RecordDrawer({ record, onClose, onApprove, onReject, onFlag }: Props) {
  const { data: history = [] } = useRecordHistory(record.id);

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer" role="dialog" aria-label="Record detail">
        {/* Header */}
        <div className="drawer-header">
          <div>
            <h6 className="fw-bold mb-0">Record Detail</h6>
            <small className="text-muted font-monospace">{record.id.slice(0, 8)}…</small>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close" />
        </div>

        <div className="drawer-body">
          {/* Status + flags */}
          <div className="d-flex align-items-center gap-2 mb-3">
            <RecordStatusBadge status={record.status} />
            <ScopeBadge scope={record.scope} />
            <SourceBadge source={record.source_type} />
            {record.is_locked && (
              <span className="badge bg-purple text-white">
                <Lock size={10} className="me-1" />Locked
              </span>
            )}
            {record.is_suspicious && (
              <span className="badge bg-warning text-dark">
                <AlertTriangle size={10} className="me-1" />Suspicious
              </span>
            )}
          </div>

          {/* Suspicious reasons */}
          {record.suspicious_reasons.length > 0 && (
            <div className="alert alert-warning py-2 mb-3">
              <div className="fw-semibold small mb-1">
                <AlertTriangle size={12} className="me-1" />Suspicious flags:
              </div>
              <ul className="mb-0 ps-3 small">
                {record.suspicious_reasons.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}

          {/* Validation errors */}
          {record.validation_errors.length > 0 && (
            <div className="alert alert-danger py-2 mb-3">
              <div className="fw-semibold small mb-1">Validation errors:</div>
              <ul className="mb-0 ps-3 small">
                {record.validation_errors.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            </div>
          )}

          {/* Core values */}
          <div className="card mb-3">
            <div className="card-header small fw-semibold py-2">Normalized Values</div>
            <div className="card-body py-2">
              <div className="row g-2 small">
                <div className="col-6">
                  <div className="text-muted">Activity</div>
                  <div className="fw-semibold">
                    {parseFloat(record.activity_value).toLocaleString()} {record.activity_unit}
                  </div>
                </div>
                <div className="col-6">
                  <div className="text-muted">CO₂e</div>
                  <div className="fw-semibold">
                    {record.co2e_kg
                      ? `${parseFloat(record.co2e_kg).toLocaleString()} kg`
                      : "Not calculated"}
                  </div>
                </div>
                <div className="col-6">
                  <div className="text-muted">Date</div>
                  <div>{format(new Date(record.activity_date), "dd MMM yyyy")}</div>
                </div>
                {record.activity_period_start && (
                  <div className="col-6">
                    <div className="text-muted">Period</div>
                    <div>
                      {format(new Date(record.activity_period_start), "dd MMM")} –{" "}
                      {record.activity_period_end
                        ? format(new Date(record.activity_period_end), "dd MMM yyyy")
                        : "?"}
                    </div>
                  </div>
                )}
                {record.vendor_name && (
                  <div className="col-6">
                    <div className="text-muted">Vendor</div>
                    <div>{record.vendor_name}</div>
                  </div>
                )}
                {record.cost_center && (
                  <div className="col-6">
                    <div className="text-muted">Cost Center</div>
                    <div>{record.cost_center}</div>
                  </div>
                )}
                {record.document_reference && (
                  <div className="col-6">
                    <div className="text-muted">Document Ref</div>
                    <div className="font-monospace small">{record.document_reference}</div>
                  </div>
                )}
                {record.facility_name && (
                  <div className="col-6">
                    <div className="text-muted">Facility</div>
                    <div>{record.facility_name}</div>
                  </div>
                )}
                {record.original_value && (
                  <div className="col-6">
                    <div className="text-muted">Original</div>
                    <div className="text-muted small">
                      {record.original_value} {record.original_unit}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Raw data */}
          <div className="card mb-3">
            <div className="card-header small fw-semibold py-2 d-flex justify-content-between">
              <span>Raw Source Data</span>
              <span className="text-muted">Row {record.row_number} · {record.batch_filename}</span>
            </div>
            <div className="card-body py-2">
              <div className="table-responsive">
                <table className="table table-sm table-borderless mb-0 small">
                  <tbody>
                    {Object.entries(record.raw_data).map(([k, v]) => (
                      <tr key={k}>
                        <td className="text-muted pe-3 text-nowrap">{k}</td>
                        <td className="font-monospace">{v || <span className="text-danger">empty</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Transformation log */}
          {record.transformation_log.length > 0 && (
            <div className="card mb-3">
              <div className="card-header small fw-semibold py-2">Transformation Log</div>
              <div className="card-body py-2">
                {record.transformation_log.map((step, i) => (
                  <div key={i} className="transform-step">
                    <div className="fw-semibold text-muted small">{step.step}</div>
                    {step.from && <div className="small">From: <code>{step.from}</code></div>}
                    {step.to && <div className="small">To: <code>{step.to}</code></div>}
                    {step.note && <div className="text-muted small">{step.note}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Approval history */}
          {history.length > 0 && (
            <div className="card mb-3">
              <div className="card-header small fw-semibold py-2">Decision History</div>
              <div className="card-body py-2">
                {(history as ApprovalWorkflow[]).map(h => (
                  <div key={h.id} className="d-flex gap-2 mb-2 small">
                    <div className="mt-1">
                      {h.decision === "approved" ? <CheckCircle size={14} className="text-success" /> :
                       h.decision === "rejected" ? <XCircle size={14} className="text-danger" /> :
                       <Flag size={14} className="text-warning" />}
                    </div>
                    <div>
                      <div>
                        <span className="fw-semibold">{h.decided_by}</span>
                        <span className="text-muted ms-1">{h.decision}</span>
                        <span className="text-muted ms-1">
                          {format(new Date(h.created_at), "dd MMM yyyy HH:mm")}
                        </span>
                      </div>
                      {h.comment && <div className="text-muted fst-italic">"{h.comment}"</div>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer actions */}
        {!record.is_locked && (
          <div className="p-3 border-top d-flex gap-2">
            <button className="btn btn-success flex-fill" onClick={onApprove}>
              <CheckCircle size={14} className="me-1" />Approve
            </button>
            <button className="btn btn-danger flex-fill" onClick={onReject}>
              <XCircle size={14} className="me-1" />Reject
            </button>
            <button className="btn btn-warning flex-fill" onClick={onFlag}>
              <Flag size={14} className="me-1" />Flag
            </button>
          </div>
        )}
        {record.is_locked && (
          <div className="p-3 border-top text-center text-muted small">
            <Lock size={14} className="me-1" />This record is audit-locked
          </div>
        )}
      </div>
    </>
  );
}
