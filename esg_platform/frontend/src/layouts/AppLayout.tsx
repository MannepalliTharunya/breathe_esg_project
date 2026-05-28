import { Outlet, NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, ClipboardCheck, Upload, Shield, LogOut, Leaf, AlertTriangle,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { authApi } from "../services/api/auth";

const NAV = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/review",    icon: ClipboardCheck,  label: "Review Records" },
  { to: "/upload",    icon: Upload,           label: "Upload Data" },
  { to: "/audit",     icon: Shield,           label: "Audit Trail" },
];

export function AppLayout() {
  const { user, refreshToken, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try { await authApi.logout(refreshToken!); } catch {}
    logout();
    navigate("/login");
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <NavLink to="/dashboard" className="sidebar-brand">
          <Leaf size={20} />
          ESG Platform
        </NavLink>

        <nav className="sidebar-nav">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) =>
              `nav-link ${isActive ? "active" : ""}`
            }>
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-top border-secondary">
          <div className="text-white-50 small mb-2 px-2">
            <div className="fw-semibold text-white">{user?.full_name}</div>
            <div className="text-capitalize opacity-75">{user?.role}</div>
          </div>
          <button
            className="nav-link w-100 text-start text-danger"
            onClick={handleLogout}
          >
            <LogOut size={16} className="me-2" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="main-content">
        <header className="topbar">
          {user?.organization_name ? (
            <span className="fw-semibold text-muted small">
              🏢 {user.organization_name}
            </span>
          ) : (
            <span className="text-warning small d-flex align-items-center gap-1">
              <AlertTriangle size={14} />
              No organization assigned — contact your admin
            </span>
          )}
          <div className="ms-auto d-flex align-items-center gap-2">
            <span className="text-muted small">{user?.email}</span>
            <span className={`badge rounded-pill ${
              user?.role === "admin" ? "bg-danger" :
              user?.role === "analyst" ? "bg-primary" : "bg-secondary"
            }`}>
              {user?.role}
            </span>
          </div>
        </header>

        {/* Block access if no org */}
        {!user?.organization ? (
          <main className="page-content">
            <div className="d-flex align-items-center justify-content-center" style={{ minHeight: 400 }}>
              <div className="text-center">
                <AlertTriangle size={48} className="text-warning mb-3" />
                <h5 className="fw-bold">No Organization Assigned</h5>
                <p className="text-muted mb-4">
                  Your account is not linked to any organization.<br />
                  Ask an admin to assign you to an organization, or sign in with an admin account.
                </p>
                <button className="btn btn-outline-danger" onClick={handleLogout}>
                  <LogOut size={14} className="me-2" />
                  Sign out and use a different account
                </button>
                <div className="mt-3 p-3 bg-light rounded text-start small">
                  <strong>Demo credentials:</strong><br />
                  Email: <code>admin@esg.local</code><br />
                  Password: <code>Admin123!</code>
                </div>
              </div>
            </div>
          </main>
        ) : (
          <main className="page-content">
            <Outlet />
          </main>
        )}
      </div>
    </div>
  );
}
