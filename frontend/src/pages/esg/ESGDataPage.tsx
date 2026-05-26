import { useState } from "react";
import { Plus, Upload, Filter } from "lucide-react";
import { useDataPoints, usePeriods } from "@/hooks/useESGData";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { DataPointModal } from "@/components/esg/DataPointModal";
import { BulkImportModal } from "@/components/esg/BulkImportModal";
import { formatDate } from "@/utils/formatters";
import type { DataPointFilters, ESGCategory, DataStatus } from "@/types/esg.types";

const CATEGORY_LABELS: Record<ESGCategory, string> = {
  E: "Environmental",
  S: "Social",
  G: "Governance",
};

export function ESGDataPage() {
  const [filters, setFilters] = useState<DataPointFilters>({ page: 1, page_size: 25 });
  const [showDataPointModal, setShowDataPointModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const { data, isLoading } = useDataPoints(filters);
  const { data: periods } = usePeriods();

  const updateFilter = (key: keyof DataPointFilters, value: string | undefined) => {
    setFilters((f) => ({ ...f, [key]: value || undefined, page: 1 }));
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">ESG Data</h1>
          <p className="text-gray-500 mt-1">Manage and track your ESG metric submissions.</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-secondary gap-2" onClick={() => setShowImportModal(true)}>
            <Upload className="w-4 h-4" aria-hidden="true" />
            Import
          </button>
          <button className="btn-primary gap-2" onClick={() => setShowDataPointModal(true)}>
            <Plus className="w-4 h-4" aria-hidden="true" />
            Add data point
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <Filter className="w-4 h-4 text-gray-400 flex-shrink-0" aria-hidden="true" />

          <select
            className="input w-auto"
            value={filters.category ?? ""}
            onChange={(e) => updateFilter("category", e.target.value as ESGCategory)}
            aria-label="Filter by category"
          >
            <option value="">All categories</option>
            {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>

          <select
            className="input w-auto"
            value={filters.period ?? ""}
            onChange={(e) => updateFilter("period", e.target.value)}
            aria-label="Filter by reporting period"
          >
            <option value="">All periods</option>
            {periods?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>

          <select
            className="input w-auto"
            value={filters.status as string ?? ""}
            onChange={(e) => updateFilter("status", e.target.value as DataStatus)}
            aria-label="Filter by status"
          >
            <option value="">All statuses</option>
            {["draft", "submitted", "under_review", "approved", "rejected", "published"].map((s) => (
              <option key={s} value={s}>{s.replace("_", " ")}</option>
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
            <table className="w-full text-sm" aria-label="ESG data points">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Metric</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Category</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Value</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Submitted</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data?.results.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-12 text-gray-400">
                      No data points found. Add your first metric.
                    </td>
                  </tr>
                ) : (
                  data?.results.map((dp) => (
                    <tr key={dp.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3">
                        <p className="font-medium text-gray-900">{dp.metric.name}</p>
                        <p className="text-xs text-gray-400">{dp.metric.code}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`badge ${
                          dp.metric.category === "E" ? "badge-green" :
                          dp.metric.category === "S" ? "badge-blue" : "bg-purple-100 text-purple-800 badge"
                        }`}>
                          {CATEGORY_LABELS[dp.metric.category]}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono text-gray-900">
                        {dp.value !== null ? `${dp.value} ${dp.metric.unit}` : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={dp.status} />
                      </td>
                      <td className="px-4 py-3 text-gray-500">
                        {dp.submitted_at ? formatDate(dp.submitted_at) : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-brand-500 rounded-full"
                              style={{ width: `${dp.confidence_level}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-500">{dp.confidence_level}%</span>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data && data.pagination.total_pages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
              <p className="text-sm text-gray-500">
                Page {data.pagination.current_page} of {data.pagination.total_pages} ({data.pagination.count} total)
              </p>
              <div className="flex gap-2">
                <button
                  className="btn-secondary text-xs px-3 py-1.5"
                  disabled={!data.pagination.previous}
                  onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) - 1 }))}
                >
                  Previous
                </button>
                <button
                  className="btn-secondary text-xs px-3 py-1.5"
                  disabled={!data.pagination.next}
                  onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) + 1 }))}
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modals */}
      {showDataPointModal && <DataPointModal onClose={() => setShowDataPointModal(false)} />}
      {showImportModal && <BulkImportModal onClose={() => setShowImportModal(false)} />}
    </div>
  );
}
