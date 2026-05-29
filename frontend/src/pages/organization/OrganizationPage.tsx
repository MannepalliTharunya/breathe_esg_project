import { useOrganizationStore } from "@/store/organizationStore";
import { useMembers, useFacilities, useDepartments } from "@/hooks/useOrganization";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { Building2, Users, MapPin } from "lucide-react";

export function OrganizationPage() {
  const { activeOrganization } = useOrganizationStore();
  const orgId = activeOrganization?.id ?? "";
  const { data: members, isLoading: membersLoading } = useMembers(orgId);
  const { data: facilities, isLoading: facilitiesLoading } = useFacilities(orgId);
  const { data: departments, isLoading: departmentsLoading } = useDepartments(orgId);

  if (!activeOrganization) {
    return (
      <div className="text-center py-16 text-gray-400">
        <Building2 className="w-12 h-12 mx-auto mb-3 opacity-40" aria-hidden="true" />
        <p>No organization selected.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{activeOrganization.name}</h1>
        <p className="text-gray-500 mt-1 capitalize">{activeOrganization.industry} · {activeOrganization.country}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Members */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-5 h-5 text-gray-400" aria-hidden="true" />
            <h3 className="font-semibold text-gray-900">Team members</h3>
            <span className="badge badge-gray ml-auto">{members?.pagination.count ?? 0}</span>
          </div>
          {membersLoading ? (
            <PageLoader />
          ) : (
            <ul className="space-y-3" aria-label="Team members">
              {members?.results.map((m: import("@/types/organization.types").Membership) => (
                <li key={m.id} className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 font-medium text-sm flex-shrink-0">
                    {m.user.full_name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{m.user.full_name}</p>
                    <p className="text-xs text-gray-400 truncate">{m.user.email}</p>
                  </div>
                  <span className="badge badge-gray capitalize">{m.role.replace("_", " ")}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Facilities */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="w-5 h-5 text-gray-400" aria-hidden="true" />
            <h3 className="font-semibold text-gray-900">Facilities</h3>
            <span className="badge badge-gray ml-auto">{facilities?.pagination.count ?? 0}</span>
          </div>
          {facilitiesLoading ? (
            <PageLoader />
          ) : (
            <ul className="space-y-3" aria-label="Facilities">
              {facilities?.results.map((f: import("@/types/organization.types").Facility) => (
                <li key={f.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50">
                  <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-4 h-4 text-gray-500" aria-hidden="true" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{f.name}</p>
                    <p className="text-xs text-gray-400">{f.city}, {f.country}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Departments */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <Building2 className="w-5 h-5 text-gray-400" aria-hidden="true" />
            <h3 className="font-semibold text-gray-900">Departments</h3>
            <span className="badge badge-gray ml-auto">{departments?.pagination?.count ?? 0}</span>
          </div>
          {departmentsLoading ? (
            <PageLoader />
          ) : !departments || departments.results?.length === 0 ? (
            <div className="text-center py-12 text-gray-400 text-sm">
              <Building2 className="w-8 h-8 mx-auto mb-2 opacity-45" />
              <p>No departments defined.</p>
            </div>
          ) : (
            <ul className="space-y-3" aria-label="Departments">
              {departments.results.map((d: any) => (
                <li key={d.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50">
                  <div className="w-8 h-8 rounded-lg bg-brand-50 flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-4 h-4 text-brand-600" aria-hidden="true" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{d.name}</p>
                    <p className="text-xs text-gray-400">Code: {d.code || "N/A"}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
