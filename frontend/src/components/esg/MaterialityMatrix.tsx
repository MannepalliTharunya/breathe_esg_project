/**
 * Double materiality matrix — plots topics by financial vs impact materiality.
 * Uses Recharts ScatterChart.
 */
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { cn } from "@/utils/cn";
import type { MaterialityAssessment } from "@/types/esg.types";

interface MaterialityMatrixProps {
  assessments: MaterialityAssessment[];
  className?: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  E: "#16a34a",
  S: "#2563eb",
  G: "#7c3aed",
};

interface TooltipPayload {
  payload: MaterialityAssessment & { x: number; y: number };
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 max-w-xs">
      <p className="font-semibold text-gray-900 text-sm">{d.topic}</p>
      <div className="mt-1 space-y-0.5 text-xs text-gray-500">
        <p>Financial materiality: <strong>{d.financial_materiality_score}</strong></p>
        <p>Impact materiality: <strong>{d.impact_materiality_score}</strong></p>
        <p>
          Category:{" "}
          <span className={cn("font-medium", {
            "text-green-600": d.category === "E",
            "text-blue-600": d.category === "S",
            "text-purple-600": d.category === "G",
          })}>
            {d.category === "E" ? "Environmental" : d.category === "S" ? "Social" : "Governance"}
          </span>
        </p>
        {d.is_material && <p className="text-brand-600 font-medium">✓ Material</p>}
      </div>
    </div>
  );
}

export function MaterialityMatrix({ assessments, className }: MaterialityMatrixProps) {
  const data = assessments.map((a) => ({
    ...a,
    x: Number(a.financial_materiality_score),
    y: Number(a.impact_materiality_score),
  }));

  return (
    <div className={cn("card p-5", className)}>
      <div className="mb-4">
        <h3 className="font-semibold text-gray-900">Double Materiality Matrix</h3>
        <p className="text-xs text-gray-500 mt-0.5">
          Financial materiality (x-axis) vs. Impact materiality (y-axis)
        </p>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mb-4 text-xs">
        {[["E", "Environmental", "#16a34a"], ["S", "Social", "#2563eb"], ["G", "Governance", "#7c3aed"]].map(
          ([cat, label, color]) => (
            <div key={cat} className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} aria-hidden="true" />
              <span className="text-gray-600">{label}</span>
            </div>
          )
        )}
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            type="number"
            dataKey="x"
            domain={[0, 10]}
            name="Financial materiality"
            label={{ value: "Financial materiality →", position: "insideBottom", offset: -10, fontSize: 11, fill: "#9ca3af" }}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            type="number"
            dataKey="y"
            domain={[0, 10]}
            name="Impact materiality"
            label={{ value: "Impact materiality →", angle: -90, position: "insideLeft", offset: 10, fontSize: 11, fill: "#9ca3af" }}
            tick={{ fontSize: 11 }}
          />
          {/* Materiality threshold lines */}
          <ReferenceLine x={5} stroke="#e5e7eb" strokeDasharray="4 4" />
          <ReferenceLine y={5} stroke="#e5e7eb" strokeDasharray="4 4" />
          <Tooltip content={<CustomTooltip />} />
          <Scatter data={data} name="Topics">
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={CATEGORY_COLORS[entry.category] ?? "#6b7280"}
                fillOpacity={entry.is_material ? 1 : 0.4}
                stroke={entry.is_material ? CATEGORY_COLORS[entry.category] : "transparent"}
                strokeWidth={2}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>

      <p className="text-xs text-gray-400 mt-2 text-center">
        Solid dots = material topics · Faded dots = not yet material
      </p>
    </div>
  );
}
