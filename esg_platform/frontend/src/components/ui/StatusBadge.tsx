import type { RecordStatus, BatchStatus } from "../../types";

const RECORD_COLORS: Record<RecordStatus, string> = {
  pending:  "bg-secondary",
  flagged:  "bg-warning text-dark",
  approved: "bg-success",
  rejected: "bg-danger",
  locked:   "bg-purple text-white",
};

const BATCH_COLORS: Record<BatchStatus, string> = {
  pending:    "bg-secondary",
  processing: "bg-info text-dark",
  completed:  "bg-success",
  failed:     "bg-danger",
  partial:    "bg-warning text-dark",
};

export function RecordStatusBadge({ status }: { status: RecordStatus }) {
  return (
    <span className={`badge ${RECORD_COLORS[status] ?? "bg-secondary"}`}>
      {status}
    </span>
  );
}

export function BatchStatusBadge({ status }: { status: BatchStatus }) {
  return (
    <span className={`badge ${BATCH_COLORS[status] ?? "bg-secondary"}`}>
      {status}
    </span>
  );
}

export function ScopeBadge({ scope }: { scope: string }) {
  const colors: Record<string, string> = {
    scope_1: "bg-danger",
    scope_2: "bg-primary",
    scope_3: "bg-warning text-dark",
  };
  const labels: Record<string, string> = {
    scope_1: "Scope 1",
    scope_2: "Scope 2",
    scope_3: "Scope 3",
  };
  return (
    <span className={`badge ${colors[scope] ?? "bg-secondary"}`}>
      {labels[scope] ?? scope}
    </span>
  );
}

export function SourceBadge({ source }: { source: string }) {
  const colors: Record<string, string> = {
    sap:     "bg-dark",
    utility: "bg-info text-dark",
    travel:  "bg-purple text-white",
  };
  return (
    <span className={`badge ${colors[source] ?? "bg-secondary"}`}>
      {source.toUpperCase()}
    </span>
  );
}
