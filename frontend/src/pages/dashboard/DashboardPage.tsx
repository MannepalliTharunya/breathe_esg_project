import { useState } from "react";
import { useESGSummary, useDashboardStats, usePeriods } from "@/hooks/useESGData";
import { useReports } from "@/hooks/useReports";
import { useMe } from "@/hooks/useAuth";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { ESGCategoryCard } from "@/components/dashboard/ESGCategoryCard";
import { EmissionsTrendChart } from "@/components/dashboard/EmissionsTrendChart";
import { RecentActivityFeed } from "@/components/dashboard/RecentActivityFeed";
import { QuickActions } from "@/components/dashboard/QuickActions";

export function DashboardPage() {
  const [periodId, setPeriodId] = useState<string>("");
  const { data: user } = useMe();
  const { data: periods } = usePeriods();
  const { data: summary, isLoading: summaryLoading } = useESGSummary(periodId || undefined);
  const { data: stats, isLoading: statsLoading } = useDashboardStats(periodId || undefined);
  const { data: reports } = useReports({ page_size: "5" });

  if (summaryLoading || statsLoading) return <PageLoader />;

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {greeting}, {user?.first_name} 👋
          </h1>
          <p className="text-gray-500 mt-1">Here's your ESG performance overview.</p>
        </div>
        <div className="w-full sm:w-64">
          <label htmlFor="dashboard-period" className="label">Reporting period</label>
          <select
            id="dashboard-period"
            className="input"
            value={periodId}
            onChange={(e) => setPeriodId(e.target.value)}
          >
            <option value="">All periods</option>
            {periods?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-5 bg-white shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div>
            <p className="text-sm font-medium text-gray-500">Total uploaded records</p>
            <h3 className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_uploaded_records ?? 0}</h3>
          </div>
        </div>
        <div className="card p-5 bg-white shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div>
            <p className="text-sm font-medium text-gray-500">Suspicious rows</p>
            <h3 className="text-3xl font-bold text-yellow-600 mt-2">{stats?.suspicious_rows ?? 0}</h3>
          </div>
          <p className="text-xs text-gray-400 mt-2">Confidence below 80%</p>
        </div>
        <div className="card p-5 bg-white shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div>
            <p className="text-sm font-medium text-gray-500">Approved rows</p>
            <h3 className="text-3xl font-bold text-green-600 mt-2">{stats?.approved_rows ?? 0}</h3>
          </div>
        </div>
        <div className="card p-5 bg-white shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div>
            <p className="text-sm font-medium text-gray-500">Failed / rejected</p>
            <h3 className="text-3xl font-bold text-red-600 mt-2">{stats?.failed_rows ?? 0}</h3>
          </div>
        </div>
      </div>

      {stats?.emissions_by_scope && (
        <div className="grid grid-cols-3 gap-4">
          {(["scope1", "scope2", "scope3"] as const).map((scope, i) => (
            <div key={scope} className="card p-4 text-center">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Scope {i + 1}</p>
              <p className="text-xl font-bold text-gray-900 mt-1">
                {(stats.emissions_by_scope[scope] ?? 0).toLocaleString(undefined, { maximumFractionDigits: 1 })}
              </p>
              <p className="text-xs text-gray-400">tCO₂e (approved)</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ESGCategoryCard category="E" label="Environmental" color="text-green-600" bgColor="bg-green-50" summary={summary?.E} />
        <ESGCategoryCard category="S" label="Social" color="text-blue-600" bgColor="bg-blue-50" summary={summary?.S} />
        <ESGCategoryCard category="G" label="Governance" color="text-purple-600" bgColor="bg-purple-50" summary={summary?.G} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <EmissionsTrendChart periodId={periodId || undefined} />
        </div>
        <div>
          <QuickActions />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivityFeed reports={reports?.results ?? []} />
      </div>
    </div>
  );
}
