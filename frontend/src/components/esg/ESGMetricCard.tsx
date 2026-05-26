/**
 * Card displaying a single ESG metric with its latest approved value,
 * trend indicator, and status.
 */
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/utils/cn";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatNumber } from "@/utils/formatters";
import type { ESGDataPoint } from "@/types/esg.types";

interface ESGMetricCardProps {
  dataPoint: ESGDataPoint;
  previousValue?: number | null;
  onClick?: () => void;
}

function TrendIndicator({ current, previous }: { current: number; previous: number | null | undefined }) {
  if (previous == null) return null;
  const delta = ((current - previous) / Math.abs(previous)) * 100;
  const isUp = delta > 0;
  const isFlat = Math.abs(delta) < 0.5;

  if (isFlat) return <Minus className="w-4 h-4 text-gray-400" aria-label="No change" />;

  return (
    <span
      className={cn("flex items-center gap-1 text-xs font-medium", isUp ? "text-red-600" : "text-green-600")}
      aria-label={`${isUp ? "Increased" : "Decreased"} by ${Math.abs(delta).toFixed(1)}%`}
    >
      {isUp ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
      {Math.abs(delta).toFixed(1)}%
    </span>
  );
}

const CATEGORY_STYLES: Record<string, { border: string; dot: string }> = {
  E: { border: "border-l-green-500", dot: "bg-green-500" },
  S: { border: "border-l-blue-500", dot: "bg-blue-500" },
  G: { border: "border-l-purple-500", dot: "bg-purple-500" },
};

export function ESGMetricCard({ dataPoint, previousValue, onClick }: ESGMetricCardProps) {
  const style = CATEGORY_STYLES[dataPoint.metric.category] ?? { border: "border-l-gray-300", dot: "bg-gray-400" };

  return (
    <button
      onClick={onClick}
      className={cn(
        "card p-4 text-left w-full border-l-4 hover:shadow-md transition-all duration-200 focus-visible:ring-2 focus-visible:ring-brand-500",
        style.border
      )}
      aria-label={`${dataPoint.metric.name}: ${dataPoint.value} ${dataPoint.metric.unit}`}
    >
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex items-center gap-2 min-w-0">
          <span className={cn("w-2 h-2 rounded-full flex-shrink-0", style.dot)} aria-hidden="true" />
          <span className="text-xs font-mono text-gray-400 truncate">{dataPoint.metric.code}</span>
        </div>
        <StatusBadge status={dataPoint.status} />
      </div>

      <p className="text-sm font-semibold text-gray-900 line-clamp-2 mb-2">
        {dataPoint.metric.name}
      </p>

      <div className="flex items-end justify-between">
        <div>
          {dataPoint.value !== null ? (
            <>
              <span className="text-xl font-bold text-gray-900">
                {typeof dataPoint.value === "number"
                  ? formatNumber(dataPoint.value)
                  : String(dataPoint.value)}
              </span>
              <span className="text-sm text-gray-400 ml-1">{dataPoint.metric.unit}</span>
            </>
          ) : (
            <span className="text-gray-400 text-sm">No value</span>
          )}
        </div>

        {typeof dataPoint.numeric_value === "number" && (
          <TrendIndicator current={dataPoint.numeric_value} previous={previousValue} />
        )}
      </div>

      {/* Confidence bar */}
      <div className="mt-3">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Confidence</span>
          <span>{dataPoint.confidence_level}%</span>
        </div>
        <div className="h-1 bg-gray-100 rounded-full overflow-hidden" role="progressbar" aria-valuenow={dataPoint.confidence_level} aria-valuemin={0} aria-valuemax={100}>
          <div
            className={cn(
              "h-full rounded-full",
              dataPoint.confidence_level >= 80 ? "bg-green-400" :
              dataPoint.confidence_level >= 50 ? "bg-yellow-400" : "bg-red-400"
            )}
            style={{ width: `${dataPoint.confidence_level}%` }}
          />
        </div>
      </div>
    </button>
  );
}
