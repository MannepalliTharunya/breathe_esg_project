import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Leaf, Eye, EyeOff } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { authApi } from "../../services/api/auth";
import { InlineSpinner } from "../../components/ui/Spinner";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await authApi.login(email, password);
      login(data.access, data.refresh, data.user);
      navigate("/dashboard");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { error?: { message?: string } } } })
        ?.response?.data?.error?.message ?? "Invalid credentials";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="card shadow-sm" style={{ width: 400 }}>
        <div className="card-body p-4">
          <div className="text-center mb-4">
            <div className="d-inline-flex align-items-center justify-content-center bg-success rounded-circle mb-3"
              style={{ width: 48, height: 48 }}>
              <Leaf size={24} className="text-white" />
            </div>
            <h4 className="fw-bold mb-0">ESG Platform</h4>
            <p className="text-muted small">Emissions Ingestion & Review</p>
          </div>

          {error && (
            <div className="alert alert-danger py-2 small">{error}</div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label fw-semibold small">Email</label>
              <input type="email" className="form-control" required
                value={email} onChange={e => setEmail(e.target.value)}
                placeholder="analyst@company.com" autoFocus />
            </div>
            <div className="mb-4">
              <label className="form-label fw-semibold small">Password</label>
              <div className="input-group">
                <input type={showPw ? "text" : "password"} className="form-control" required
                  value={password} onChange={e => setPassword(e.target.value)} />
                <button type="button" className="btn btn-outline-secondary"
                  onClick={() => setShowPw(s => !s)}>
                  {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>
            <button type="submit" className="btn btn-success w-100" disabled={loading}>
              {loading ? <><InlineSpinner />Signing in…</> : "Sign in"}
            </button>
          </form>

          <div className="text-center mt-3 small text-muted">
            No account?{" "}
            <Link to="/register" className="text-success">Register</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
