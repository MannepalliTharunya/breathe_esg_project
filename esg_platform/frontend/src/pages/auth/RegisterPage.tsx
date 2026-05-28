import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Leaf } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { authApi } from "../../services/api/auth";
import { InlineSpinner } from "../../components/ui/Spinner";

export function RegisterPage() {
  const [form, setForm] = useState({
    email: "", first_name: "", last_name: "",
    password: "", password_confirm: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.password_confirm) {
      setError("Passwords do not match");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const data = await authApi.register({ ...form, role: "analyst" });
      login(data.access, data.refresh, data.user);
      navigate("/dashboard");
    } catch (err: unknown) {
      const details = (err as { response?: { data?: { error?: { details?: Record<string, string[]> } } } })
        ?.response?.data?.error?.details;
      if (details) {
        const msgs = Object.entries(details).map(([k, v]) => `${k}: ${v.join(", ")}`).join("; ");
        setError(msgs);
      } else {
        setError("Registration failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="card shadow-sm" style={{ width: 440 }}>
        <div className="card-body p-4">
          <div className="text-center mb-4">
            <div className="d-inline-flex align-items-center justify-content-center bg-success rounded-circle mb-3"
              style={{ width: 48, height: 48 }}>
              <Leaf size={24} className="text-white" />
            </div>
            <h4 className="fw-bold mb-0">Create Account</h4>
          </div>

          {error && <div className="alert alert-danger py-2 small">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="row g-2 mb-2">
              <div className="col">
                <label className="form-label small fw-semibold">First name</label>
                <input className="form-control form-control-sm" required
                  value={form.first_name} onChange={set("first_name")} />
              </div>
              <div className="col">
                <label className="form-label small fw-semibold">Last name</label>
                <input className="form-control form-control-sm" required
                  value={form.last_name} onChange={set("last_name")} />
              </div>
            </div>
            <div className="mb-2">
              <label className="form-label small fw-semibold">Email</label>
              <input type="email" className="form-control form-control-sm" required
                value={form.email} onChange={set("email")} />
            </div>
            <div className="mb-2">
              <label className="form-label small fw-semibold">Password</label>
              <input type="password" className="form-control form-control-sm" required
                value={form.password} onChange={set("password")} />
            </div>
            <div className="mb-3">
              <label className="form-label small fw-semibold">Confirm password</label>
              <input type="password" className="form-control form-control-sm" required
                value={form.password_confirm} onChange={set("password_confirm")} />
            </div>
            <button type="submit" className="btn btn-success w-100" disabled={loading}>
              {loading ? <><InlineSpinner />Creating account…</> : "Create account"}
            </button>
          </form>

          <div className="text-center mt-3 small text-muted">
            Already have an account?{" "}
            <Link to="/login" className="text-success">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
