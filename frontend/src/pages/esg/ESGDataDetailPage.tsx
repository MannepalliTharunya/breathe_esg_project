import { useParams } from "react-router-dom";
import { useDataPoint, useUpdateDataPointStatus } from "@/hooks/useESGData";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDate } from "@/utils/formatters";

export function ESGDataDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: dp, isLoading } = useDataPoint(id!);
  const updateStatus = useUpdateDataPointStatus();

  if (isLoading) return <PageLoader />;
  if (!dp) return <div className="text-center py-12 text-gray-400">Data point not found.</div>;

  return (
    <div className="max-w-3xl space-y-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{dp.metric.name}</h1>
          <p className="text-gray-500 mt-1">{dp.metric.code} · {dp.metric.unit}</p>
        </div>
        <StatusBadge status={dp.status} />
      </div>

      <div className="card p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Value</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {dp.value !== null ? `${dp.value} ${dp.metric.unit}` : "—"}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Confidence</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{dp.confidence_level}%</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Collection method</p>
            <p className="text-sm text-gray-700 mt-1 capitalize">{dp.collection_method}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Data source</p>
            <p className="text-sm text-gray-700 mt-1">{dp.data_source || "—"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Submitted by</p>
            <p className="text-sm text-gray-700 mt-1">{dp.submitted_by_name || "—"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Submitted at</p>
            <p className="text-sm text-gray-700 mt-1">{dp.submitted_at ? formatDate(dp.submitted_at) : "—"}</p>
          </div>
        </div>

        {dp.notes && (
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Notes</p>
            <p className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">{dp.notes}</p>
          </div>
        )}

        {dp.review_notes && (
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Review notes</p>
            <p className="text-sm text-gray-700 bg-yellow-50 rounded-lg p-3 border border-yellow-100">
              {dp.review_notes}
            </p>
          </div>
        )}
      </div>

      {/* Workflow actions */}
      {dp.status === "submitted" && (
        <div className="card p-4 flex gap-3">
          <button
            className="btn-primary"
            onClick={() => updateStatus.mutate({ id: dp.id, status: "approved" })}
            disabled={updateStatus.isPending}
          >
            Approve
          </button>
          <button
            className="btn-danger"
            onClick={() => updateStatus.mutate({ id: dp.id, status: "rejected" })}
            disabled={updateStatus.isPending}
          >
            Reject
          </button>
        </div>
      )}
    </div>
  );
}
