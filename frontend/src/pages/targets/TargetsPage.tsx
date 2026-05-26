import { useTargets } from "@/hooks/useESGData";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { Target, TrendingDown } from "lucide-react";

export function TargetsPage() {
  const { data, isLoading } = useTargets();

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">ESG Targets</h1>
        <p className="text-gray-500 mt-1">Track progress toward your science-based and internal targets.</p>
      </div>

      {data?.results.length === 0 ? (
        <div className="card text-center py-16 text-gray-400">
          <Target className="w-12 h-12 mx-auto mb-3 opacity-40" aria-hidden="true" />
          <p className="font-medium">No targets defined</p>
          <p className="text-sm mt-1">Set your first ESG target to start tracking progress.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data?.results.map((target) => (
            <div key={target.id} className="card p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{target.name}</h3>
                  <p className="text-sm text-gray-500 mt-0.5">{target.metric_name}</p>
                </div>
                {target.is_science_based && (
                  <span className="badge badge-green">Science-based</span>
                )}
              </div>

              <div className="grid grid-cols-3 gap-3 text-center mb-4">
                <div>
                  <p className="text-xs text-gray-400">Baseline ({target.baseline_year})</p>
                  <p className="font-semibold text-gray-900">{target.baseline_value} {target.metric_unit}</p>
                </div>
                <div className="flex items-center justify-center">
                  <TrendingDown className="w-5 h-5 text-green-500" aria-hidden="true" />
                </div>
                <div>
                  <p className="text-xs text-gray-400">Target ({target.target_year})</p>
                  <p className="font-semibold text-gray-900">{target.target_value} {target.metric_unit}</p>
                </div>
              </div>

              {target.progress_percentage !== null && (
                <div>
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Progress</span>
                    <span>{target.progress_percentage}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden" role="progressbar" aria-valuenow={target.progress_percentage} aria-valuemin={0} aria-valuemax={100}>
                    <div
                      className="h-full bg-brand-500 rounded-full transition-all"
                      style={{ width: `${target.progress_percentage}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
