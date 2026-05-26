import { useQuery } from "@tanstack/react-query";
import apiClient from "@/services/api/client";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { BookOpen, ExternalLink } from "lucide-react";

function useFrameworks() {
  return useQuery({
    queryKey: ["frameworks"],
    queryFn: () => apiClient.get("/frameworks/").then((r) => r.data),
  });
}

export function FrameworksPage() {
  const { data, isLoading } = useFrameworks();

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reporting Frameworks</h1>
        <p className="text-gray-500 mt-1">Manage the ESG frameworks your organization reports against.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data?.results?.map((fw: { id: string; code: string; name: string; version: string; description: string; issuing_body: string; website: string; requirement_count: number }) => (
          <div key={fw.id} className="card p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="w-10 h-10 rounded-lg bg-brand-50 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-brand-600" aria-hidden="true" />
              </div>
              <span className="badge badge-blue">{fw.version}</span>
            </div>
            <h3 className="font-semibold text-gray-900">{fw.code}</h3>
            <p className="text-sm text-gray-500 mt-0.5">{fw.name}</p>
            <p className="text-xs text-gray-400 mt-2 line-clamp-2">{fw.description}</p>
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
              <span className="text-xs text-gray-500">{fw.requirement_count} requirements</span>
              {fw.website && (
                <a
                  href={fw.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-brand-600 flex items-center gap-1 hover:underline"
                >
                  Learn more <ExternalLink className="w-3 h-3" aria-hidden="true" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
