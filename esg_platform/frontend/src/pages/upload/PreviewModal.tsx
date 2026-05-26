import { useQuery } from "@tanstack/react-query";
import { X } from "lucide-react";
import { ingestionApi } from "../../services/api/ingestion";
import { Spinner } from "../../components/ui/Spinner";
import type { RawRecord } from "../../types";

interface Props {
  batchId: string;
  onClose: () => void;
}

export function PreviewModal({ batchId, onClose }: Props) {
  const { data: rows = [], isLoading } = useQuery<RawRecord[]>({
    queryKey: ["ingestion", "preview", batchId],
    queryFn: () => ingestionApi.preview(batchId),
  });

  const headers = rows.length > 0 ? Object.keys(rows[0].raw_data) : [];

  return (
    <div className="modal d-block" style={{ background: "rgba(0,0,0,0.5)" }}>
      <div className="modal-dialog modal-xl modal-dialog-scrollable">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">CSV Preview (first 20 rows)</h5>
            <button className="btn-close" onClick={onClose} />
          </div>
          <div className="modal-body p-0">
            {isLoading ? <Spinner /> : (
              <div className="table-responsive">
                <table className="table table-sm table-bordered mb-0 small">
                  <thead className="table-dark">
                    <tr>
                      <th>#</th>
                      <th>Status</th>
                      {headers.map(h => <th key={h}>{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map(row => (
                      <tr key={row.id} className={row.parse_errors.length > 0 ? "table-danger" : ""}>
                        <td>{row.row_number}</td>
                        <td>
                          <span className={`badge ${row.status === "failed" ? "bg-danger" : "bg-secondary"}`}>
                            {row.status}
                          </span>
                          {row.parse_errors.length > 0 && (
                            <div className="text-danger small">{row.parse_errors.join("; ")}</div>
                          )}
                        </td>
                        {headers.map(h => (
                          <td key={h} className={!row.raw_data[h] ? "text-danger" : ""}>
                            {row.raw_data[h] || <em>empty</em>}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button className="btn btn-secondary" onClick={onClose}>Close</button>
          </div>
        </div>
      </div>
    </div>
  );
}
