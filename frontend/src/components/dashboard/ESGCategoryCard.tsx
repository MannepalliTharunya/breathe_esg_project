import { cn } from "@/utils/cn";
import type { CategorySummary } from "@/types/esg.types";

interface ESGCategoryCardProps {
  category: "E" | "S" | "G";
  label: string;
  color: string;
  bgColor: string;
  summary?: CategorySummary;
}

export function ESGCategoryCard({ category, label, color, bgColor, summary }: ESGCategoryCardProps) {
  const pct = summary?.completion_pct ?? 0;

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg", bgColor, color)}>
          {category}
        </div>
        <span className={cn("text-2xl font-bold", color)}>{pct}%</span>
      </div>

      <h3 className="font-semibold text-gray-900">{label}</h3>
      <p className="text-sm text-gray-500 mt-0.5">
        {summary?.approved ?? 0} of {summary?.total_metrics ?? 0} metrics approved
      </p>

      {/* Progress bar */}
      <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <div
          className={cn("h-full rounded-full transition-all duration-500", {
            "bg-green-500": category === "E",
            "bg-blue-500": category === "S",
            "bg-purple-500": category === "G",
          })}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
