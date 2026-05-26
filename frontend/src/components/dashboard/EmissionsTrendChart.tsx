import { useAnalytics } from "@/hooks/useESGData";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export function EmissionsTrendChart() {
  const { data: analytics, isLoading } = useAnalytics();

  const trendData = analytics?.emissions_trend?.length > 0 ? analytics.emissions_trend : [];

  return (
    <div className="card p-5">
      <h3 className="font-semibold text-gray-900 mb-4">GHG Emissions Trend (tCO₂e)</h3>
      {isLoading ? (
        <div className="h-[260px] flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : trendData.length === 0 ? (
        <div className="h-[260px] flex flex-col items-center justify-center text-gray-400">
          <p className="font-medium text-sm">No emissions data available</p>
          <p className="text-xs mt-1">Submit Scope 1, 2, and 3 GHG data to see trends.</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={trendData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="year" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
            <Tooltip
              formatter={(value: number) => [`${value.toLocaleString()} tCO₂e`]}
              contentStyle={{ borderRadius: "8px", border: "1px solid #e5e7eb" }}
            />
            <Legend />
            <Line type="monotone" dataKey="scope1" name="Scope 1" stroke="#16a34a" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="scope2" name="Scope 2" stroke="#2563eb" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="scope3" name="Scope 3" stroke="#7c3aed" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
