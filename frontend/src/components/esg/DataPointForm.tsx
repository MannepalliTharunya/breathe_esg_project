/**
 * Form for creating or editing a single ESG data point.
 * Handles numeric, text, and boolean metric types.
 */
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMetrics, usePeriods, useCreateDataPoint } from "@/hooks/useESGData";
import { useFacilities } from "@/hooks/useOrganization";
import { useCollectionMethods, useDataSources } from "@/hooks/useMasterData";
import { useOrganizationStore } from "@/store/organizationStore";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import type { MetricDefinition } from "@/types/esg.types";

const schema = z.object({
  metric: z.string().uuid("Select a metric"),
  reporting_period: z.string().uuid("Select a reporting period"),
  facility: z.string().optional().or(z.literal("")),
  numeric_value: z.string().optional(),
  text_value: z.string().optional(),
  boolean_value: z.string().optional(),
  data_source: z.string().min(1, "Select a data source"),
  collection_method: z.string().min(1, "Select a collection method"),
  confidence_level: z.coerce.number().min(0).max(100),
  notes: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

interface DataPointFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function DataPointForm({ onSuccess, onCancel }: DataPointFormProps) {
  const { activeOrganizationId } = useOrganizationStore();
  const { data: metricsData, isLoading: metricsLoading, isError: metricsError } = useMetrics();
  const { data: periodsData, isLoading: periodsLoading, isError: periodsError } = usePeriods();
  const { data: facilitiesData, isLoading: facilitiesLoading } = useFacilities(activeOrganizationId ?? "");
  const { data: methodsData, isLoading: methodsLoading } = useCollectionMethods();
  const { data: sourcesData, isLoading: sourcesLoading } = useDataSources();
  const createDataPoint = useCreateDataPoint();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { confidence_level: 100 },
  });

  const selectedMetricId = watch("metric");
  const selectedMetric = metricsData?.results.find((m: MetricDefinition) => m.id === selectedMetricId);

  const onSubmit = (data: FormData) => {
    const payload: Record<string, unknown> = {
      metric: data.metric,
      reporting_period: data.reporting_period,
      collection_method: data.collection_method,
      confidence_level: data.confidence_level,
      data_source: data.data_source,
      notes: data.notes,
    };

    if (data.facility) {
      payload.facility = data.facility;
    }

    if (selectedMetric?.data_type === "numeric" && data.numeric_value) {
      payload.numeric_value = parseFloat(data.numeric_value);
    } else if (selectedMetric?.data_type === "boolean") {
      payload.boolean_value = data.boolean_value === "true";
    } else {
      payload.text_value = data.text_value;
    }

    createDataPoint.mutate(payload as Parameters<typeof createDataPoint.mutate>[0], {
      onSuccess: () => onSuccess?.(),
    });
  };

  const isLoading = metricsLoading || periodsLoading || facilitiesLoading || methodsLoading || sourcesLoading;

  if (isLoading) return <LoadingSpinner />;

  const noMetrics = !metricsData?.results?.length;
  const noPeriods = !periodsData?.results?.length;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
      {(metricsError || periodsError) && (
        <p className="text-sm text-red-600" role="alert">
          Could not load form options. Check that an organization is selected.
        </p>
      )}

      {noPeriods && (
        <p className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
          No reporting periods found. Run database seed or create a period for this organization.
        </p>
      )}

      {/* Metric */}
      <div>
        <label htmlFor="metric" className="label">Metric <span className="text-red-500">*</span></label>
        <select
          id="metric"
          className="input"
          aria-describedby={errors.metric ? "metric-error" : undefined}
          aria-invalid={!!errors.metric}
          disabled={noMetrics}
          {...register("metric")}
        >
          <option value="">{noMetrics ? "No metrics available" : "Select a metric…"}</option>
          {metricsData?.results.map((m: MetricDefinition) => (
            <option key={m.id} value={m.id}>
              [{m.category}] {m.code} — {m.name}
            </option>
          ))}
        </select>
        {errors.metric && (
          <p id="metric-error" className="mt-1 text-xs text-red-600" role="alert">{errors.metric.message}</p>
        )}
      </div>

      {/* Reporting Period */}
      <div>
        <label htmlFor="reporting_period" className="label">Reporting period <span className="text-red-500">*</span></label>
        <select
          id="reporting_period"
          className="input"
          aria-invalid={!!errors.reporting_period}
          disabled={noPeriods}
          {...register("reporting_period")}
        >
          <option value="">{noPeriods ? "No periods available" : "Select a period…"}</option>
          {periodsData?.results.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        {errors.reporting_period && (
          <p className="mt-1 text-xs text-red-600" role="alert">{errors.reporting_period.message}</p>
        )}
      </div>

      {/* Facility */}
      <div>
        <label htmlFor="facility" className="label">Facility</label>
        <select id="facility" className="input" {...register("facility")}>
          <option value="">All facilities / not specified</option>
          {facilitiesData?.results.map((f) => (
            <option key={f.id} value={f.id}>{f.name}</option>
          ))}
        </select>
      </div>

      {/* Dynamic value field based on metric type */}
      {selectedMetric && (
        <div>
          <label className="label">
            Value <span className="text-red-500">*</span>
            {selectedMetric.unit && (
              <span className="ml-1 text-gray-400 font-normal">({selectedMetric.unit})</span>
            )}
          </label>

          {selectedMetric.data_type === "numeric" && (
            <input
              type="number"
              step="any"
              className="input"
              placeholder="Enter numeric value"
              {...register("numeric_value")}
            />
          )}

          {selectedMetric.data_type === "text" && (
            <textarea
              className="input min-h-[80px] resize-y"
              placeholder="Enter text value"
              {...register("text_value")}
            />
          )}

          {selectedMetric.data_type === "boolean" && (
            <select className="input" {...register("boolean_value")}>
              <option value="">Select…</option>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          )}

          {selectedMetric.data_type === "percentage" && (
            <div className="relative">
              <input
                type="number"
                step="0.01"
                min="0"
                max="100"
                className="input pr-8"
                placeholder="0–100"
                {...register("numeric_value")}
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">%</span>
            </div>
          )}
        </div>
      )}

      {/* Collection method + confidence */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="collection_method" className="label">Collection method <span className="text-red-500">*</span></label>
          <select id="collection_method" className="input" {...register("collection_method")}>
            <option value="">Select method…</option>
            {methodsData?.results.map((m) => (
              <option key={m.id} value={m.code}>{m.name}</option>
            ))}
          </select>
          {errors.collection_method && (
            <p className="mt-1 text-xs text-red-600" role="alert">{errors.collection_method.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="confidence_level" className="label">Confidence (%)</label>
          <input
            id="confidence_level"
            type="number"
            min="0"
            max="100"
            className="input"
            {...register("confidence_level")}
          />
        </div>
      </div>

      {/* Data source */}
      <div>
        <label htmlFor="data_source" className="label">Data source <span className="text-red-500">*</span></label>
        <select id="data_source" className="input" {...register("data_source")}>
          <option value="">Select source…</option>
          {sourcesData?.results.map((s) => (
            <option key={s.id} value={s.code}>{s.name}</option>
          ))}
        </select>
        {errors.data_source && (
          <p className="mt-1 text-xs text-red-600" role="alert">{errors.data_source.message}</p>
        )}
      </div>

      {/* Notes */}
      <div>
        <label htmlFor="notes" className="label">Notes</label>
        <textarea
          id="notes"
          className="input min-h-[80px] resize-y"
          placeholder="Any additional context or methodology notes…"
          {...register("notes")}
        />
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          className="btn-primary"
          disabled={createDataPoint.isPending || noMetrics || noPeriods}
        >
          {createDataPoint.isPending ? "Submitting…" : "Submit data point"}
        </button>
        {onCancel && (
          <button type="button" className="btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
