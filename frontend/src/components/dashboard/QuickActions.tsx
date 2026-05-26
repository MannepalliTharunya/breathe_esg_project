import { Link } from "react-router-dom";
import { Plus, Upload, FileText, Target } from "lucide-react";

const ACTIONS = [
  { to: "/esg/data?action=new", icon: Plus, label: "Add data point", description: "Submit a new ESG metric" },
  { to: "/esg/data?action=import", icon: Upload, label: "Bulk import", description: "Upload CSV or Excel" },
  { to: "/reports?action=new", icon: FileText, label: "Generate report", description: "Create a GRI, TCFD, or SASB report" },
  { to: "/targets?action=new", icon: Target, label: "Set target", description: "Define a new ESG target" },
];

export function QuickActions() {
  return (
    <div className="card p-5">
      <h3 className="font-semibold text-gray-900 mb-4">Quick actions</h3>
      <div className="space-y-2">
        {ACTIONS.map(({ to, icon: Icon, label, description }) => (
          <Link
            key={to}
            to={to}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <div className="w-8 h-8 rounded-lg bg-brand-50 flex items-center justify-center group-hover:bg-brand-100 transition-colors">
              <Icon className="w-4 h-4 text-brand-600" aria-hidden="true" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">{label}</p>
              <p className="text-xs text-gray-500">{description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
