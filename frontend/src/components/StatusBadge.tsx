import type { UseCaseStatus } from "../api/types";

const STATUS_CONFIG: Record<UseCaseStatus, { label: string; classes: string }> = {
  new: { label: "Neu", classes: "bg-blue-100 text-blue-700" },
  in_review: { label: "In Bewertung", classes: "bg-yellow-100 text-yellow-700" },
  approved: { label: "Genehmigt", classes: "bg-green-100 text-green-700" },
  in_progress: { label: "In Umsetzung", classes: "bg-purple-100 text-purple-700" },
  completed: { label: "Abgeschlossen", classes: "bg-gray-100 text-gray-700" },
  archived: { label: "Archiviert", classes: "bg-red-100 text-red-700" },
};

export default function StatusBadge({ status }: { status: UseCaseStatus }) {
  const config = STATUS_CONFIG[status];
  return (
    <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded-full ${config.classes}`}>
      {config.label}
    </span>
  );
}

export { STATUS_CONFIG };
