import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Download, RefreshCw } from "lucide-react";
import { useReport, useRegenerateReport } from "@/hooks/useReports";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { formatDate, formatBytes } from "@/utils/formatters";

export function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: report, isLoading } = useReport(id!);
  const regenerate = useRegenerateReport();

  if (isLoading) return <PageLoader />;
  if (!report) return <div className="text-center py-12 text-gray-400">Report not found.</div>;

  return (
    <div className="max-w-2xl space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <Link to="/reports" className="btn-ghost p-2" aria-label="Back to reports">
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">{report.name}</h1>
      </div>

      <div className="card p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Framework</p>
            <p className="text-sm font-medium text-gray-900 mt-1 capitalize">{report.report_type}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Status</p>
            <p className="text-sm font-medium text-gray-900 mt-1 capitalize">{report.status}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Created</p>
            <p className="text-sm text-gray-700 mt-1">{formatDate(report.created_at)}</p>
          </div>
          {report.generated_at && (
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wider">Generated</p>
              <p className="text-sm text-gray-700 mt-1">{formatDate(report.generated_at)}</p>
            </div>
          )}
          {report.file_size_bytes && (
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wider">File size</p>
              <p className="text-sm text-gray-700 mt-1">{formatBytes(report.file_size_bytes)}</p>
            </div>
          )}
        </div>

        {report.error_message && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{report.error_message}</p>
          </div>
        )}

        {report.status === "generating" && (
          <div className="flex items-center gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="w-4 h-4 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-yellow-700">Report is being generated…</p>
          </div>
        )}

        <div className="flex gap-3 pt-2">
          {report.status === "ready" && report.file_url && (
            <a href={report.file_url} download className="btn-primary gap-2">
              <Download className="w-4 h-4" aria-hidden="true" />
              Download PDF
            </a>
          )}
          <button
            className="btn-secondary gap-2"
            onClick={() => regenerate.mutate(report.id)}
            disabled={regenerate.isPending || report.status === "generating"}
          >
            <RefreshCw className="w-4 h-4" aria-hidden="true" />
            Regenerate
          </button>
        </div>
      </div>
    </div>
  );
}
