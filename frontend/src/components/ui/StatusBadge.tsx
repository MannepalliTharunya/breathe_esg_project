import { cn } from "@/utils/cn";
import type { DataStatus } from "@/types/esg.types";

const STATUS_CONFIG: Record<DataStatus, { label: string; className: string }> = {
  draft: { label: "Draft", className: "badge-gray" },
  submitted: { label: "Submitted", className: "badge-blue" },
  under_review: { label: "Under Review", className: "badge-yellow" },
  approved: { label: "Approved", className: "badge-green" },
  rejected: { label: "Rejected", className: "badge-red" },
  published: { label: "Published", className: "bg-purple-100 text-purple-800 badge" },
};

interface StatusBadgeProps {
  status: DataStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? { label: status, className: "badge-gray" };
  return (
    <span className={cn(config.className, className)} aria-label={`Status: ${config.label}`}>
      {config.label}
    </span>
  );
}
