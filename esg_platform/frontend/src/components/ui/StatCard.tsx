import type { ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: number | string;
  icon?: ReactNode;
  color?: string;
  subtitle?: string;
  onClick?: () => void;
}

export function StatCard({ label, value, icon, color = "text-success", subtitle, onClick }: StatCardProps) {
  return (
    <div
      className={`stat-card ${onClick ? "cursor-pointer" : ""}`}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="d-flex align-items-start justify-content-between">
        <div>
          <div className={`stat-value ${color}`}>{value}</div>
          <div className="stat-label">{label}</div>
          {subtitle && <div className="text-muted small mt-1">{subtitle}</div>}
        </div>
        {icon && <div className={`${color} opacity-50`}>{icon}</div>}
      </div>
    </div>
  );
}
