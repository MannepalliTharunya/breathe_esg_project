import { useState } from "react";
import { Plus, FileText, Download, RefreshCw } from "lucide-react";
import { useReports, useCreateReport, useRegenerateReport } from "@/hooks/useReports";
import { usePeriods } from "@/hooks/useESGData";
import { useFrameworks } from "@/hooks/useFrameworks";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { formatDate } from "@/utils/formatters";
import { formatBytes } from "@/utils/formatters";

const STATUS_STYLES: Record<string, string> = {
  ready: "badge-green",
  generating: "badge-yellow",
  failed: "badge-red",
  published: "bg-purple-100 text-purple-800 badge",
  draft: "badge-gray",
};

export function ReportsPage() {
  const { data, isLoading } = useReports();
  const { data: periods, isLoading: periodsLoading } = usePeriods();
  const { data: frameworks, isLoading: frameworksLoading } = useFrameworks();
  const createReport = useCreateReport();
  const regenerate = useRegenerateReport();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", report_type: "gri", reporting_period: "" });

  const frameworkOptions = frameworks?.results ?? [];
  const reportTypeLabel = (code: string) =>
    frameworkOptions.find((f: { code: string; name: string }) => f.code === code)?.name ?? code.toUpperCase();

  const handleCreate = () => {
    if (!form.name || !form.reporting_period) return;
    createReport.mutate(
      { name: form.name, report_type: form.report_type as "gri", reporting_period: form.reporting_period },
      { onSuccess: () => setShowForm(false) }
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-500 mt-1">Generate and manage your ESG disclosure reports.</p>
        </div>
        <button className="btn-primary gap-2" onClick={() => setShowForm(true)}>
          <Plus className="w-4 h-4" aria-hidden="true" />
          New report
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <div className="card p-5 space-y-4 animate-slide-up">
          <h3 className="font-semibold text-gray-900">Generate new report</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Report name</label>
              <input
                type="text"
                className="input"
                placeholder="e.g. 2024 Annual GRI Report"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              />
            </div>
            <div>
              <label className="label">Framework</label>
              <select
                className="input"
                value={form.report_type}
                onChange={(e) => setForm((f) => ({ ...f, report_type: e.target.value }))}
                disabled={frameworksLoading}
              >
                {frameworkOptions.length === 0 ? (
                  <option value="gri">GRI Standards</option>
                ) : (
                  frameworkOptions.map((fw: { id: string; code: string; name: string }) => (
                    <option key={fw.id} value={fw.code}>{fw.name}</option>
                  ))
                )}
              </select>
            </div>
            <div>
              <label className="label">Reporting period</label>
              <select
                className="input"
                value={form.reporting_period}
                onChange={(e) => setForm((f) => ({ ...f, reporting_period: e.target.value }))}
                disabled={periodsLoading}
              >
                <option value="">{periodsLoading ? "Loading…" : "Select period"}</option>
                {periods?.results.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="btn-primary" onClick={handleCreate} disabled={createReport.isPending}>
              {createReport.isPending ? "Generating..." : "Generate report"}
            </button>
            <button className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      {/* Reports list */}
      {isLoading ? (
        <PageLoader />
      ) : (
        <div className="card overflow-hidden">
          {data?.results.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-40" aria-hidden="true" />
              <p className="font-medium">No reports yet</p>
              <p className="text-sm mt-1">Generate your first ESG report above.</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-100" aria-label="Reports list">
              {data?.results.map((report: import("@/types/reports.types").Report) => (
                <li key={report.id} className="flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition-colors">
                  <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-gray-500" aria-hidden="true" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{report.name}</p>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-xs text-gray-400">{reportTypeLabel(report.report_type)}</span>
                      <span className="text-xs text-gray-300">·</span>
                      <span className="text-xs text-gray-400">{formatDate(report.created_at)}</span>
                      {report.file_size_bytes && (
                        <>
                          <span className="text-xs text-gray-300">·</span>
                          <span className="text-xs text-gray-400">{formatBytes(report.file_size_bytes)}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <span className={STATUS_STYLES[report.status] ?? "badge-gray"}>{report.status}</span>
                  <div className="flex items-center gap-2">
                    {report.status === "ready" && report.file_url && (
                      <a
                        href={report.file_url}
                        download
                        className="btn-ghost p-2"
                        aria-label={`Download ${report.name}`}
                      >
                        <Download className="w-4 h-4" aria-hidden="true" />
                      </a>
                    )}
                    {report.status !== "generating" && (
                      <button
                        className="btn-ghost p-2"
                        onClick={() => regenerate.mutate(report.id)}
                        aria-label={`Regenerate ${report.name}`}
                      >
                        <RefreshCw className="w-4 h-4" aria-hidden="true" />
                      </button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
