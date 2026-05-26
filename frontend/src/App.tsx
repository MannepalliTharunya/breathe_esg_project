import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "./components/ui/Toaster";
import { AuthGuard } from "./components/auth/AuthGuard";
import { AppLayout } from "./layouts/AppLayout";
import { AuthLayout } from "./layouts/AuthLayout";

// Pages
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { ForgotPasswordPage } from "./pages/auth/ForgotPasswordPage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { ESGDataPage } from "./pages/esg/ESGDataPage";
import { ESGDataDetailPage } from "./pages/esg/ESGDataDetailPage";
import { ReportsPage } from "./pages/reports/ReportsPage";
import { ReportDetailPage } from "./pages/reports/ReportDetailPage";
import { TargetsPage } from "./pages/targets/TargetsPage";
import { FrameworksPage } from "./pages/frameworks/FrameworksPage";
import { OrganizationPage } from "./pages/organization/OrganizationPage";
import { SettingsPage } from "./pages/settings/SettingsPage";
import { AuditLogPage } from "./pages/audit/AuditLogPage";
import { NotFoundPage } from "./pages/NotFoundPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public auth routes */}
        <Route element={<AuthLayout />}>
          <Route path="/auth/login" element={<LoginPage />} />
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
        </Route>

        {/* Protected app routes */}
        <Route element={<AuthGuard />}>
          <Route element={<AppLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/esg/data" element={<ESGDataPage />} />
            <Route path="/esg/data/:id" element={<ESGDataDetailPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/reports/:id" element={<ReportDetailPage />} />
            <Route path="/targets" element={<TargetsPage />} />
            <Route path="/frameworks" element={<FrameworksPage />} />
            <Route path="/organization" element={<OrganizationPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/audit" element={<AuditLogPage />} />
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  );
}
