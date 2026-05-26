import { Link } from "react-router-dom";
import { FileText, Clock } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { Report } from "@/types/reports.types";

const REPORT_STATUS_COLORS: Record<string, string> = {
  ready: "badge-green",
  generating: "badge-yellow",
  failed: "badge-red",
  published: "bg-purple-100 text-purple-800 badge",
  draft: "badge-gray",
};

interface RecentActivityFeedProps {
  reports: Report[];
}

export function RecentActivityFeed({ reports }: RecentActivityFeedProps) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">Recent reports</h3>
        <Link to="/reports" className="text-sm text-brand-600 hover:underline">View all</Link>
      </div>

      {reports.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" aria-hidden="true" />
          <p className="text-sm">No reports yet</p>
        </div>
      ) : (
        <ul className="space-y-3" aria-label="Recent reports">
          {reports.map((report) => (
            <li key={report.id}>
              <Link
                to={`/reports/${report.id}`}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                  <FileText className="w-4 h-4 text-gray-500" aria-hidden="true" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{report.name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className={REPORT_STATUS_COLORS[report.status] ?? "badge-gray"}>
                      {report.status}
                    </span>
                    <span className="text-xs text-gray-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" aria-hidden="true" />
                      {formatDistanceToNow(new Date(report.created_at), { addSuffix: true })}
                    </span>
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
