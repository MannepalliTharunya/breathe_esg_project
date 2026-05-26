import { Outlet } from "react-router-dom";
import { Sidebar } from "@/components/navigation/Sidebar";
import { TopBar } from "@/components/navigation/TopBar";
import { useUIStore } from "@/store/uiStore";
import { useOrganizationInit } from "@/hooks/useOrganizationInit";
import { cn } from "@/utils/cn";

export function AppLayout() {
  const { sidebarOpen } = useUIStore();
  useOrganizationInit(); // bootstrap active org

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <div
        className={cn(
          "flex flex-1 flex-col overflow-hidden transition-all duration-300",
          sidebarOpen ? "ml-64" : "ml-16"
        )}
      >
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
