import { Outlet, NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, ClipboardCheck, Upload, Shield, LogOut, Leaf,
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
            <div className="text-capitalize">{user?.role}</div>
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
          <span className="fw-semibold text-muted small">
            {user?.organization_name ?? "No organization"}
          </span>
          <div className="ms-auto d-flex align-items-center gap-2">
            <span className={`badge rounded-pill ${
              user?.role === "admin" ? "bg-danger" :
              user?.role === "analyst" ? "bg-primary" : "bg-secondary"
            }`}>
              {user?.role}
            </span>
          </div>
        </header>
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
