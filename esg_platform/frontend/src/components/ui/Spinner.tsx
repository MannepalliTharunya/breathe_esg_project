export function Spinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sz = size === "sm" ? "spinner-border-sm" : size === "lg" ? "spinner-border-lg" : "";
  return (
    <div className="spinner-overlay">
      <div className={`spinner-border text-success ${sz}`} role="status">
        <span className="visually-hidden">Loading…</span>
      </div>
    </div>
  );
}

export function InlineSpinner() {
  return (
    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
  );
}
