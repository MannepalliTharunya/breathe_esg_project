/**
 * Organization switcher — shown in the sidebar when the user belongs to multiple orgs.
 */
import { ChevronDown, Building2 } from "lucide-react";
import { useState } from "react";
import { useOrganizationStore } from "@/store/organizationStore";
import { cn } from "@/utils/cn";

export function OrgSelector() {
  const { organizations, activeOrganization, setActiveOrganization } = useOrganizationStore();
  const [open, setOpen] = useState(false);

  if (organizations.length <= 1) return null;

  return (
    <div className="relative px-3 py-2 border-b border-gray-100">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-2 text-left hover:bg-gray-50 rounded-lg px-2 py-1.5 transition-colors"
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-label="Switch organization"
      >
        <Building2 className="w-4 h-4 text-gray-400 flex-shrink-0" aria-hidden="true" />
        <span className="flex-1 text-sm font-medium text-gray-700 truncate">
          {activeOrganization?.name ?? "Select organization"}
        </span>
        <ChevronDown className={cn("w-3.5 h-3.5 text-gray-400 transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <ul
          className="absolute left-3 right-3 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 py-1 animate-fade-in"
          role="listbox"
          aria-label="Organizations"
        >
          {organizations.map((org) => (
            <li key={org.id} role="option" aria-selected={org.id === activeOrganization?.id}>
              <button
                className={cn(
                  "w-full text-left px-3 py-2 text-sm transition-colors",
                  org.id === activeOrganization?.id
                    ? "bg-brand-50 text-brand-700 font-medium"
                    : "text-gray-700 hover:bg-gray-50"
                )}
                onClick={() => { setActiveOrganization(org); setOpen(false); }}
              >
                {org.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
