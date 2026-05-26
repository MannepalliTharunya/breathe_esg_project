import { useState, useCallback } from "react";
import { AlertTriangle, Filter, RefreshCw, CheckCircle, XCircle, Flag } from "lucide-react";
import { useRecords, useApprove, useReject, useFlag, useBulkAction } from "../../hooks/useReview";
import { RecordStatusBadge, ScopeBadge, SourceBadge } from "../../components/ui/StatusBadge";
import { Spinner, InlineSpinner } from "../../components/ui/Spinner";
import { RecordDrawer } from "./RecordDrawer";
import type { NormalizedRecord, RecordStatus, Scope } from "../../types";
import { format } from "date-fns";

const STATUS_OPTIONS: RecordStatus[] = ["pending", "flagged", "approved", "rejected", "locked"];
const SCOPE_OPTIONS: Scope[] = ["scope_1", "scope_2", "scope_3"];
const SOURCE_OPTIONS = ["sap", "utility", "travel"];

export function ReviewPage() {
  const [filters, setFilters] = useState<Record<string, string | boolean | number>>({
    page: 1, page_size: 50,
  });
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [drawerRecord, setDrawerRecord] = useState<NormalizedRecord | null>(null);
  const [commentModal, setCommentModal] = useState<{ action: string; ids: string[] } | null>(null);
  const [comment, setComment] = useState("");

  const { data, isLoading, isFetching, refetch } = useRecords(filters);
  const approve = useApprove();
  const reject = useReject();
  const flag = useFlag();
  const bulk = useBulkAction();

  const records = data?.results ?? [];
  const totalPages = data?.total_pages ?? 1;
  const currentPage = data?.current_page ?? 1;

  const toggleSelect = useCallback((id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  const toggleAll = () => {
    if (selectedIds.size === records.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(records.map(r => r.id)));
    }
  };

  const openAction = (action: string, ids: string[]) => {
    setCommentModal({ action, ids });
    setComment("");
  };

  const executeAction = async () => {
    if (!commentModal) return;
    const { action, ids } = commentModal;
    if (ids.length === 1) {
      const id = ids[0];
      if (action === "approved") await approve.mutateAsync({ id, comment });
      else if (action === "rejected") await reject.mutateAsync({ id, comment });
      else if (action === "flagged") await flag.mutateAsync({ id, comment });
    } else {
      await bulk.mutateAsync({ ids, decision: action, comment });
    }
    setCommentModal(null);
    setSelectedIds(new Set());
    if (drawerRecord && ids.includes(drawerRecord.id)) setDrawerRecord(null);
  };

  const setFilter = (key: string, value: string | boolean | number | undefined) => {
    setFilters(f => {
      const next = { ...f, page: 1 };
      if (value === undefined || value === "") {
        delete next[key];
      } else {
        next[key] = value;
      }
      return next;
    });
  };

  return (
    <div>
      <div className="d-flex align-items-center justify-content-between mb-3">
        <div>
          <h4 className="fw-bold mb-0">Review Records</h4>
          <p className="text-muted small mb-0">
            {data?.count ?? 0} records · {isFetching && "refreshing…"}
          </p>
        </div>
        <button className="btn btn-outline-secondary btn-sm" onClick={() => refetch()}>
          <RefreshCw size={14} className="me-1" />
          Refresh
        </button>
      </div>

      {/* ── Filters ─────────────────────────────────────────────────────── */}
      <div className="card mb-3">
        <div className="card-body py-2">
          <div className="row g-2 align-items-end">
            <div className="col-auto">
              <Filter size={14} className="text-muted me-1" />
              <small className="text-muted fw-semibold">FILTERS</small>
            </div>
            <div className="col-auto">
              <select className="form-select form-select-sm"
                value={String(filters.status ?? "")}
                onChange={e => setFilter("status", e.target.value)}>
                <option value="">All statuses</option>
                {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="col-auto">
              <select className="form-select form-select-sm"
                value={String(filters.scope ?? "")}
                onChange={e => setFilter("scope", e.target.value)}>
                <option value="">All scopes</option>
                {SCOPE_OPTIONS.map(s => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
              </select>
            </div>
            <div className="col-auto">
              <select className="form-select form-select-sm"
                value={String(filters.source_type ?? "")}
                onChange={e => setFilter("source_type", e.target.value)}>
                <option value="">All sources</option>
                {SOURCE_OPTIONS.map(s => <option key={s} value={s}>{s.toUpperCase()}</option>)}
              </select>
            </div>
            <div className="col-auto">
              <div className="form-check form-check-inline mb-0">
                <input className="form-check-input" type="checkbox" id="suspicious-filter"
                  checked={filters.is_suspicious === true}
                  onChange={e => setFilter("is_suspicious", e.target.checked ? true : undefined)} />
                <label className="form-check-label small" htmlFor="suspicious-filter">
                  <AlertTriangle size={12} className="text-warning me-1" />
                  Suspicious only
                </label>
              </div>
            </div>
            <div className="col">
              <input className="form-control form-control-sm" placeholder="Search vendor, cost center…"
                value={String(filters.search ?? "")}
                onChange={e => setFilter("search", e.target.value)} />
            </div>
            <div className="col-auto">
              <input type="date" className="form-control form-control-sm"
                value={String(filters.date_from ?? "")}
                onChange={e => setFilter("date_from", e.target.value)} />
            </div>
            <div className="col-auto">
              <input type="date" className="form-control form-control-sm"
                value={String(filters.date_to ?? "")}
                onChange={e => setFilter("date_to", e.target.value)} />
            </div>
          </div>
        </div>
      </div>

      {/* ── Bulk actions ─────────────────────────────────────────────────── */}
      {selectedIds.size > 0 && (
        <div className="alert alert-info d-flex align-items-center gap-3 py-2 mb-3">
          <span className="fw-semibold">{selectedIds.size} selected</span>
          <button className="btn btn-success btn-sm"
            onClick={() => openAction("approved", [...selectedIds])}>
            <CheckCircle size={14} className="me-1" />Approve all
          </button>
          <button className="btn btn-danger btn-sm"
            onClick={() => openAction("rejected", [...selectedIds])}>
            <XCircle size={14} className="me-1" />Reject all
          </button>
          <button className="btn btn-warning btn-sm"
            onClick={() => openAction("flagged", [...selectedIds])}>
            <Flag size={14} className="me-1" />Flag all
          </button>
          <button className="btn btn-outline-secondary btn-sm ms-auto"
            onClick={() => setSelectedIds(new Set())}>
            Clear
          </button>
        </div>
      )}

      {/* ── Table ────────────────────────────────────────────────────────── */}
      {isLoading ? <Spinner /> : (
        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover records-table mb-0">
              <thead className="table-light">
                <tr>
                  <th style={{ width: 40 }}>
                    <input type="checkbox" className="form-check-input"
                      checked={selectedIds.size === records.length && records.length > 0}
                      onChange={toggleAll} />
                  </th>
                  <th>Date</th>
                  <th>Source</th>
                  <th>Scope</th>
                  <th>Activity</th>
                  <th>CO₂e (kg)</th>
                  <th>Vendor / Ref</th>
                  <th>Facility</th>
                  <th>Status</th>
                  <th>Flags</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.length === 0 ? (
                  <tr>
                    <td colSpan={11} className="text-center text-muted py-5">
                      No records match the current filters.
                    </td>
                  </tr>
                ) : records.map(record => (
                  <tr
                    key={record.id}
                    className={record.is_suspicious ? "row-suspicious" : ""}
                    onClick={() => setDrawerRecord(record)}
                    style={{ cursor: "pointer" }}
                  >
                    <td onClick={e => e.stopPropagation()}>
                      <input type="checkbox" className="form-check-input"
                        checked={selectedIds.has(record.id)}
                        onChange={() => toggleSelect(record.id)} />
                    </td>
                    <td className="text-nowrap">
                      {format(new Date(record.activity_date), "dd MMM yyyy")}
                    </td>
                    <td><SourceBadge source={record.source_type} /></td>
                    <td><ScopeBadge scope={record.scope} /></td>
                    <td className="text-nowrap">
                      <span className="fw-mono">
                        {parseFloat(record.activity_value).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                      </span>
                      <span className="text-muted ms-1 small">{record.activity_unit}</span>
                    </td>
                    <td className="text-nowrap">
                      {record.co2e_kg
                        ? parseFloat(record.co2e_kg).toLocaleString(undefined, { maximumFractionDigits: 2 })
                        : <span className="text-muted">—</span>}
                    </td>
                    <td>
                      <div className="text-truncate" style={{ maxWidth: 160 }}>
                        {record.vendor_name || record.document_reference || "—"}
                      </div>
                    </td>
                    <td>{record.facility_name ?? "—"}</td>
                    <td><RecordStatusBadge status={record.status} /></td>
                    <td>
                      {record.is_suspicious && (
                        <AlertTriangle size={14} className="text-warning" title={record.suspicious_reasons.join("; ")} />
                      )}
                      {record.validation_errors.length > 0 && (
                        <span className="badge bg-danger ms-1">{record.validation_errors.length} err</span>
                      )}
                    </td>
                    <td onClick={e => e.stopPropagation()}>
                      {!record.is_locked && (
                        <div className="d-flex gap-1">
                          <button className="btn btn-success btn-sm py-0 px-1"
                            title="Approve"
                            onClick={() => openAction("approved", [record.id])}>
                            <CheckCircle size={12} />
                          </button>
                          <button className="btn btn-danger btn-sm py-0 px-1"
                            title="Reject"
                            onClick={() => openAction("rejected", [record.id])}>
                            <XCircle size={12} />
                          </button>
                          <button className="btn btn-warning btn-sm py-0 px-1"
                            title="Flag"
                            onClick={() => openAction("flagged", [record.id])}>
                            <Flag size={12} />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="card-footer d-flex align-items-center justify-content-between">
              <small className="text-muted">
                Page {currentPage} of {totalPages} · {data?.count} total
              </small>
              <div className="d-flex gap-1">
                <button className="btn btn-outline-secondary btn-sm"
                  disabled={currentPage <= 1}
                  onClick={() => setFilters(f => ({ ...f, page: currentPage - 1 }))}>
                  ← Prev
                </button>
                <button className="btn btn-outline-secondary btn-sm"
                  disabled={currentPage >= totalPages}
                  onClick={() => setFilters(f => ({ ...f, page: currentPage + 1 }))}>
                  Next →
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Record detail drawer ─────────────────────────────────────────── */}
      {drawerRecord && (
        <RecordDrawer
          record={drawerRecord}
          onClose={() => setDrawerRecord(null)}
          onApprove={() => openAction("approved", [drawerRecord.id])}
          onReject={() => openAction("rejected", [drawerRecord.id])}
          onFlag={() => openAction("flagged", [drawerRecord.id])}
        />
      )}

      {/* ── Comment modal ────────────────────────────────────────────────── */}
      {commentModal && (
        <div className="modal d-block" style={{ background: "rgba(0,0,0,0.5)" }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title text-capitalize">
                  {commentModal.action} {commentModal.ids.length > 1 ? `${commentModal.ids.length} records` : "record"}
                </h5>
                <button className="btn-close" onClick={() => setCommentModal(null)} />
              </div>
              <div className="modal-body">
                <label className="form-label">Comment (optional)</label>
                <textarea
                  className="form-control"
                  rows={3}
                  placeholder="Add a note for the audit trail…"
                  value={comment}
                  onChange={e => setComment(e.target.value)}
                />
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={() => setCommentModal(null)}>
                  Cancel
                </button>
                <button
                  className={`btn ${
                    commentModal.action === "approved" ? "btn-success" :
                    commentModal.action === "rejected" ? "btn-danger" : "btn-warning"
                  }`}
                  onClick={executeAction}
                  disabled={approve.isPending || reject.isPending || flag.isPending || bulk.isPending}
                >
                  {(approve.isPending || reject.isPending || flag.isPending || bulk.isPending) && <InlineSpinner />}
                  Confirm {commentModal.action}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
