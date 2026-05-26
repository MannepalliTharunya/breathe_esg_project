import { useState } from "react";
import { Shield, Filter } from "lucide-react";
import { useAuditLogs } from "@/hooks/useAudit";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { formatDateTime } from "@/utils/formatters";
import type { AuditAction } from "@/types/audit.types";

const ACTION_STYLES: Record<AuditAction, string> = {
  create: "badge-green",
  update: "badge-blue",
  delete: "badge-red",
  login: "badge-gray",
  logout: "badge-gray",
  export: "badge-yellow",
  approve: "badge-green",
  reject: "badge-red",
  publish: "bg-purple-100 text-purple-800 badge",
  import: "badge-blue",
};

export function AuditLogPage() {
  const [filters, setFilters] = useState<Record<string, string>>({});
  const { data, isLoading } = useAuditLogs(filters);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <Shield className="w-6 h-6 text-gray-400" aria-hidden="true" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
          <p className="text-gray-500 mt-0.5">Immutable record of all platform actions.</p>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <Filter className="w-4 h-4 text-gray-400 flex-shrink-0" aria-hidden="true" />
          <select
            className="input w-auto"
            value={filters.action ?? ""}
            onChange={(e) => setFilters((f) => ({ ...f, action: e.target.value || "" }))}
            aria-label="Filter by action"
          >
            <option value="">All actions</option>
            {["create", "update", "delete", "login", "logout", "approve", "reject", "export", "import", "publish"].map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
          <select
            className="input w-auto"
            value={filters.resource_type ?? ""}
            onChange={(e) => setFilters((f) => ({ ...f, resource_type: e.target.value || "" }))}
            aria-label="Filter by resource type"
          >
            <option value="">All resources</option>
            {["esg", "reports", "users", "organizations", "frameworks"].map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      {isLoading ? (
        <PageLoader />
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Audit log entries">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Timestamp</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">User</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Action</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Resource</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">IP Address</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data?.results.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-12 text-gray-400">No audit log entries found.</td>
                  </tr>
                ) : (
                  data?.results.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 text-gray-500 whitespace-nowrap text-xs">
                        {formatDateTime(log.created_at)}
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-gray-900 text-xs">{log.user_email || "System"}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className={ACTION_STYLES[log.action] ?? "badge-gray"}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-gray-700 text-xs font-mono">
                          {log.resource_type}
                          {log.resource_id && <span className="text-gray-400"> /{log.resource_id.slice(0, 8)}…</span>}
                        </p>
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs font-mono">
                        {log.ip_address ?? "—"}
                      </td>
                      <td className="px-4 py-3">
                        <span className={log.status_code && log.status_code < 400 ? "badge-green" : "badge-red"}>
                          {log.status_code ?? "—"}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {data && data.pagination.total_pages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
              <p className="text-sm text-gray-500">
                {data.pagination.count} total entries
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
