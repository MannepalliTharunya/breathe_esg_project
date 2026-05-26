import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Shield, Filter } from "lucide-react";
import { auditApi } from "../../services/api/audit";
import { Spinner } from "../../components/ui/Spinner";
import type { AuditLog, PaginatedResponse } from "../../types";
import { format } from "date-fns";

const ACTION_COLORS: Record<string, string> = {
  create:          "bg-success",
  update:          "bg-primary",
  delete:          "bg-danger",
  record_approved: "bg-success",
  record_rejected: "bg-danger",
  record_flagged:  "bg-warning text-dark",
};

export function AuditPage() {
  const [filters, setFilters] = useState<Record<string, string>>({});

  const { data, isLoading } = useQuery<PaginatedResponse<AuditLog>>({
    queryKey: ["audit", "logs", filters],
    queryFn: () => auditApi.getLogs(filters),
  });

  const logs = data?.results ?? [];

  return (
    <div>
      <div className="d-flex align-items-center gap-2 mb-3">
        <Shield size={20} className="text-muted" />
        <div>
          <h4 className="fw-bold mb-0">Audit Trail</h4>
          <p className="text-muted small mb-0">Immutable record of all platform actions</p>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-3">
        <div className="card-body py-2">
          <div className="row g-2 align-items-center">
            <div className="col-auto">
              <Filter size={14} className="text-muted" />
            </div>
            <div className="col-auto">
              <select className="form-select form-select-sm"
                value={filters.action ?? ""}
                onChange={e => setFilters(f => ({ ...f, action: e.target.value }))}>
                <option value="">All actions</option>
                <option value="create">Create</option>
                <option value="update">Update</option>
                <option value="delete">Delete</option>
                <option value="record_approved">Approved</option>
                <option value="record_rejected">Rejected</option>
                <option value="record_flagged">Flagged</option>
              </select>
            </div>
            <div className="col-auto">
              <select className="form-select form-select-sm"
                value={filters.resource_type ?? ""}
                onChange={e => setFilters(f => ({ ...f, resource_type: e.target.value }))}>
                <option value="">All resources</option>
                <option value="ingestion">Ingestion</option>
                <option value="normalization">Normalization</option>
                <option value="organizations">Organizations</option>
                <option value="auth">Auth</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {isLoading ? <Spinner /> : (
        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover table-sm mb-0">
              <thead className="table-light">
                <tr>
                  <th>Timestamp</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Resource</th>
                  <th>Resource ID</th>
                  <th>IP</th>
                  <th>Before → After</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center text-muted py-5">No audit logs found</td>
                  </tr>
                ) : logs.map(log => (
                  <tr key={log.id}>
                    <td className="text-nowrap small text-muted">
                      {format(new Date(log.created_at), "dd MMM yyyy HH:mm:ss")}
                    </td>
                    <td className="small">
                      <div>{log.user_name}</div>
                      <div className="text-muted">{log.user_email}</div>
                    </td>
                    <td>
                      <span className={`badge ${ACTION_COLORS[log.action] ?? "bg-secondary"}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="small">{log.resource_type}</td>
                    <td className="font-monospace small text-muted">
                      {log.resource_id ? log.resource_id.slice(0, 8) + "…" : "—"}
                    </td>
                    <td className="small text-muted">{log.ip_address ?? "—"}</td>
                    <td className="small">
                      {Object.keys(log.before_value).length > 0 && (
                        <span className="text-muted me-1">
                          {JSON.stringify(log.before_value).slice(0, 40)}
                        </span>
                      )}
                      {Object.keys(log.after_value).length > 0 && (
                        <span className="text-success">
                          → {JSON.stringify(log.after_value).slice(0, 40)}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data && data.total_pages > 1 && (
            <div className="card-footer text-muted small">
              {data.count} total entries
            </div>
          )}
        </div>
      )}
    </div>
  );
}
