import { cn } from "@/utils/cn";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  label?: string;
}

const SIZES = {
  sm: "w-4 h-4 border-2",
  md: "w-8 h-8 border-2",
  lg: "w-12 h-12 border-4",
};

export function LoadingSpinner({ size = "md", className, label = "Loading..." }: LoadingSpinnerProps) {
  return (
    <div className={cn("flex items-center justify-center", className)} role="status" aria-label={label}>
      <div
        className={cn(
          "rounded-full border-gray-200 border-t-brand-600 animate-spin",
          SIZES[size]
        )}
      />
      <span className="sr-only">{label}</span>
    </div>
  );
}

export function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <LoadingSpinner size="lg" />
    </div>
  );
}
