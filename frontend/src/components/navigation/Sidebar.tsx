import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Database,
  FileText,
  Target,
  BookOpen,
  Building2,
  Settings,
  Shield,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useUIStore } from "@/store/uiStore";
import { OrgSelector } from "./OrgSelector";
import { cn } from "@/utils/cn";

const NAV_ITEMS = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/esg/data", icon: Database, label: "ESG Data" },
  { to: "/reports", icon: FileText, label: "Reports" },
  { to: "/targets", icon: Target, label: "Targets" },
  { to: "/frameworks", icon: BookOpen, label: "Frameworks" },
  { to: "/organization", icon: Building2, label: "Organization" },
  { to: "/audit", icon: Shield, label: "Audit Log" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 h-full bg-white border-r border-gray-200 flex flex-col transition-all duration-300 z-30",
        sidebarOpen ? "w-64" : "w-16"
      )}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-gray-200">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-600 flex-shrink-0">
          <span className="text-white font-bold text-sm">E</span>
        </div>
        {sidebarOpen && (
          <span className="ml-3 font-semibold text-gray-900 truncate">ESG Platform</span>
        )}
      </div>

      {/* Org selector */}
      {sidebarOpen && <OrgSelector />}

      {/* Nav */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-brand-50 text-brand-700"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )
            }
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={toggleSidebar}
        className="flex items-center justify-center h-12 border-t border-gray-200 text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-colors"
        aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
      >
        {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>
    </aside>
  );
}
