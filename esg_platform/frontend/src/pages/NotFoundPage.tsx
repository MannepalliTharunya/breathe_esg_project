import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center">
      <div className="text-center">
        <h1 className="display-1 fw-bold text-muted">404</h1>
        <p className="lead">Page not found</p>
        <Link to="/dashboard" className="btn btn-success">Back to Dashboard</Link>
      </div>
    </div>
  );
}
