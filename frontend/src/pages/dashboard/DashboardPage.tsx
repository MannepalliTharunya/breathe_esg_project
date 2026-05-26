import { useESGSummary, useDashboardStats } from "@/hooks/useESGData";
import { useReports } from "@/hooks/useReports";
import { useMe } from "@/hooks/useAuth";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { ESGCategoryCard } from "@/components/dashboard/ESGCategoryCard";
import { EmissionsTrendChart } from "@/components/dashboard/EmissionsTrendChart";
import { RecentActivityFeed } from "@/components/dashboard/RecentActivityFeed";
import { QuickActions } from "@/components/dashboard/QuickActions";

export function DashboardPage() {
  const { data: user } = useMe();
  const { data: summary, isLoading: summaryLoading } = useESGSummary();
  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: reports } = useReports({ page_size: "5" });

  if (summaryLoading || statsLoading) return <PageLoader />;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Good morning, {user?.first_name} 👋
        </h1>
        <p className="text-gray-500 mt-1">Here's your ESG performance overview.</p>
      </div>

      {/* KPI Stats widgets */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-5 bg-white shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div>
            <p className="text-sm font-medium text-gray-500">Total Uploaded Records</p>
            <h3 className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_uploaded_records ?? 0}</h3>
          </div>
          <p className="text-xs text-gray-400 mt-2">Cumulative count of raw audit entries</p>
        </div>
        <div className="card p-5 bg-white shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div>
            <p className="text-sm font-medium text-gray-500">Suspicious Rows</p>
            <h3 className="text-3xl font-bold text-yellow-600 mt-2">{stats?.suspicious_rows ?? 0}</h3>
          </div>
          <p className="text-xs text-gray-400 mt-2">Confidence level flagged below 80%</p>
        </div>
        <div className="card p-5 bg-white shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div>
            <p className="text-sm font-medium text-gray-500">Approved Rows</p>
            <h3 className="text-3xl font-bold text-green-600 mt-2">{stats?.approved_rows ?? 0}</h3>
          </div>
          <p className="text-xs text-gray-400 mt-2">Verified data points in system</p>
        </div>
        <div className="card p-5 bg-white shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div>
            <p className="text-sm font-medium text-gray-500">Failed / Rejected Rows</p>
            <h3 className="text-3xl font-bold text-red-600 mt-2">{stats?.failed_rows ?? 0}</h3>
          </div>
          <p className="text-xs text-gray-400 mt-2">Failed workflow validation</p>
        </div>
      </div>

      {/* ESG Category Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ESGCategoryCard
          category="E"
          label="Environmental"
          color="text-green-600"
          bgColor="bg-green-50"
          summary={summary?.E}
        />
        <ESGCategoryCard
          category="S"
          label="Social"
          color="text-blue-600"
          bgColor="bg-blue-50"
          summary={summary?.S}
        />
        <ESGCategoryCard
          category="G"
          label="Governance"
          color="text-purple-600"
          bgColor="bg-purple-50"
          summary={summary?.G}
        />
      </div>

      {/* Charts + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <EmissionsTrendChart />
        </div>
        <div>
          <QuickActions />
        </div>
      </div>

      {/* Recent Reports */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivityFeed reports={reports?.results ?? []} />
      </div>
    </div>
  );
}
