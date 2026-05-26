import { useState } from "react";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import {
  Database, AlertTriangle, CheckCircle, Clock, XCircle,
  Lock, TrendingUp, Zap,
} from "lucide-react";
import { StatCard } from "../../components/ui/StatCard";
import { Spinner } from "../../components/ui/Spinner";
import {
  useDashboard, useMonthlyTrend, useEmissionsBySource,
  useFacilityEmissions, useIngestionQuality,
} from "../../hooks/useAnalytics";

const SCOPE_COLORS: Record<string, string> = {
  scope_1: "#dc3545",
  scope_2: "#0d6efd",
  scope_3: "#fd7e14",
};

const SCOPE_LABELS: Record<string, string> = {
  scope_1: "Scope 1",
  scope_2: "Scope 2",
  scope_3: "Scope 3",
};

export function DashboardPage() {
  const { data: summary, isLoading } = useDashboard();
  const { data: monthly = [] } = useMonthlyTrend();
  const { data: bySource = [] } = useEmissionsBySource();
  const { data: byFacility = [] } = useFacilityEmissions();
  const { data: quality = [] } = useIngestionQuality();

  if (isLoading) return <Spinner />;

  const r = summary?.records;
  const e = summary?.emissions;

  // Pivot monthly data for recharts
  const monthlyPivot = monthly.reduce<Record<string, Record<string, number>>>((acc, item) => {
    if (!acc[item.month]) acc[item.month] = { month: item.month as unknown as number };
    acc[item.month][item.scope] = item.co2e_kg;
    return acc;
  }, {});
  const monthlyData = Object.values(monthlyPivot).sort((a, b) =>
    String(a.month).localeCompare(String(b.month))
  );

  return (
    <div>
      <div className="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h4 className="fw-bold mb-0">ESG Analyst Dashboard</h4>
          <p className="text-muted small mb-0">Real-time emissions data overview</p>
        </div>
        <div className="text-end">
          <div className="fw-bold fs-5 text-success">
            {e?.total_co2e_kg ? `${(e.total_co2e_kg / 1000).toFixed(1)} tCO₂e` : "—"}
          </div>
          <div className="text-muted small">Total approved emissions</div>
        </div>
      </div>

      {/* ── Record status widgets ─────────────────────────────────────────── */}
      <div className="row g-3 mb-4">
        <div className="col-6 col-md-3">
          <StatCard
            label="Total Records"
            value={r?.total ?? 0}
            icon={<Database size={28} />}
            color="text-primary"
          />
        </div>
        <div className="col-6 col-md-3">
          <StatCard
            label="Pending Review"
            value={r?.pending ?? 0}
            icon={<Clock size={28} />}
            color="text-secondary"
          />
        </div>
        <div className="col-6 col-md-3">
          <StatCard
            label="Suspicious"
            value={r?.suspicious ?? 0}
            icon={<AlertTriangle size={28} />}
            color="text-warning"
            subtitle="Needs analyst attention"
          />
        </div>
        <div className="col-6 col-md-3">
          <StatCard
            label="Flagged"
            value={r?.flagged ?? 0}
            icon={<AlertTriangle size={28} />}
            color="text-warning"
          />
        </div>
        <div className="col-6 col-md-3">
          <StatCard
            label="Approved"
            value={r?.approved ?? 0}
            icon={<CheckCircle size={28} />}
            color="text-success"
          />
        </div>
        <div className="col-6 col-md-3">
          <StatCard
            label="Rejected"
            value={r?.rejected ?? 0}
            icon={<XCircle size={28} />}
            color="text-danger"
          />
        </div>
        <div className="col-6 col-md-3">
          <StatCard
            label="Audit Locked"
            value={r?.locked ?? 0}
            icon={<Lock size={28} />}
            color="text-purple"
          />
        </div>
        <div className="col-6 col-md-3">
          <StatCard
            label="Failed Rows"
            value={r?.failed ?? 0}
            icon={<XCircle size={28} />}
            color="text-danger"
            subtitle="Parse / normalization errors"
          />
        </div>
      </div>

      {/* ── Charts row 1 ─────────────────────────────────────────────────── */}
      <div className="row g-3 mb-4">
        {/* Emissions by scope pie */}
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-header fw-semibold">Emissions by Scope</div>
            <div className="card-body">
              {e?.by_scope && e.by_scope.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={e.by_scope.map(s => ({
                        name: SCOPE_LABELS[s.scope] ?? s.scope,
                        value: s.co2e_kg,
                      }))}
                      cx="50%" cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {e.by_scope.map(s => (
                        <Cell key={s.scope} fill={SCOPE_COLORS[s.scope] ?? "#6c757d"} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v: number) => `${v.toFixed(0)} kg CO₂e`} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center text-muted py-5">No approved emissions yet</div>
              )}
            </div>
          </div>
        </div>

        {/* Monthly trend */}
        <div className="col-md-8">
          <div className="card h-100">
            <div className="card-header fw-semibold">Monthly Emissions Trend (kg CO₂e)</div>
            <div className="card-body">
              {monthlyData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
                    <Tooltip formatter={(v: number) => `${v.toFixed(0)} kg`} />
                    <Legend />
                    <Line type="monotone" dataKey="scope_1" name="Scope 1" stroke="#dc3545" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="scope_2" name="Scope 2" stroke="#0d6efd" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="scope_3" name="Scope 3" stroke="#fd7e14" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center text-muted py-5">No trend data yet</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Charts row 2 ─────────────────────────────────────────────────── */}
      <div className="row g-3 mb-4">
        {/* Emissions by source */}
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-header fw-semibold">Emissions by Source</div>
            <div className="card-body">
              {bySource.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={bySource}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="source_type" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
                    <Tooltip formatter={(v: number) => `${v.toFixed(0)} kg CO₂e`} />
                    <Bar dataKey="co2e_kg" name="CO₂e (kg)" fill="#198754" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center text-muted py-5">No data</div>
              )}
            </div>
          </div>
        </div>

        {/* Ingestion quality */}
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-header fw-semibold">Ingestion Quality</div>
            <div className="card-body">
              {quality.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-sm mb-0">
                    <thead>
                      <tr>
                        <th>Source</th>
                        <th className="text-end">Total</th>
                        <th className="text-end text-danger">Failed %</th>
                        <th className="text-end text-warning">Suspicious %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {quality.map(q => (
                        <tr key={q.source_type}>
                          <td className="text-uppercase fw-semibold">{q.source_type}</td>
                          <td className="text-end">{q.total_rows.toLocaleString()}</td>
                          <td className="text-end">
                            <span className={q.failed_pct > 10 ? "text-danger fw-bold" : "text-muted"}>
                              {q.failed_pct}%
                            </span>
                          </td>
                          <td className="text-end">
                            <span className={q.suspicious_pct > 5 ? "text-warning fw-bold" : "text-muted"}>
                              {q.suspicious_pct}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center text-muted py-5">No ingestion data yet</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Facility emissions */}
      {byFacility.length > 0 && (
        <div className="card mb-4">
          <div className="card-header fw-semibold">Top Facilities by Emissions</div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={byFacility.slice(0, 10)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="facility_name" tick={{ fontSize: 11 }} width={120} />
                <Tooltip formatter={(v: number) => `${v.toFixed(0)} kg CO₂e`} />
                <Bar dataKey="co2e_kg" name="CO₂e (kg)" fill="#0d6efd" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
