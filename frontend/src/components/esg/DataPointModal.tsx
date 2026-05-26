import { X } from "lucide-react";
import { DataPointForm } from "./DataPointForm";

interface DataPointModalProps {
  onClose: () => void;
}

export function DataPointModal({ onClose }: DataPointModalProps) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="dp-modal-title"
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto animate-slide-up">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 sticky top-0 bg-white z-10">
          <h2 id="dp-modal-title" className="font-semibold text-gray-900">Add ESG data point</h2>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600 rounded" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6">
          <DataPointForm onSuccess={onClose} onCancel={onClose} />
        </div>
      </div>
    </div>
  );
}
