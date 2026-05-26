import { User, LogOut, ChevronDown } from "lucide-react";
import { useMe, useLogout } from "@/hooks/useAuth";
import { NotificationsPanel } from "@/components/notifications/NotificationsPanel";
import { cn } from "@/utils/cn";
import { useState } from "react";

export function TopBar() {
  const { data: user } = useMe();
  const logout = useLogout();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center gap-4">
        {/* Breadcrumb or page title can go here */}
      </div>

      <div className="flex items-center gap-3">
        {/* Notifications */}
        <NotificationsPanel />

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setMenuOpen((o) => !o)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-expanded={menuOpen}
            aria-haspopup="true"
          >
            <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center">
              <User className="w-4 h-4 text-brand-600" />
            </div>
            {user && (
              <span className="text-sm font-medium text-gray-700 hidden sm:block">
                {user.full_name}
              </span>
            )}
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg border border-gray-200 shadow-lg py-1 z-50 animate-fade-in">
              <div className="px-4 py-2 border-b border-gray-100">
                <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
              <button
                onClick={() => logout.mutate()}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
