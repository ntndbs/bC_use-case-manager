import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../api/client";
import type { UseCase, UseCaseStatus } from "../api/types";
import { STATUS_CONFIG } from "../components/StatusBadge";

const ALLOWED_TRANSITIONS: Record<UseCaseStatus, UseCaseStatus[]> = {
  new: ["in_review"],
  in_review: ["approved", "new"],
  approved: ["in_progress", "in_review"],
  in_progress: ["completed", "approved"],
  completed: ["archived"],
  archived: [],
};

export default function UseCaseEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [uc, setUc] = useState<UseCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  // Form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [expectedBenefit, setExpectedBenefit] = useState("");

  useEffect(() => {
    api
      .get<UseCase>(`/use-cases/${id}`)
      .then((data) => {
        setUc(data);
        setTitle(data.title);
        setDescription(data.description);
        setExpectedBenefit(data.expected_benefit || "");
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSave() {
    setSaving(true);
    setError("");
    try {
      await api.patch(`/use-cases/${id}`, {
        title,
        description,
        expected_benefit: expectedBenefit || null,
      });
      navigate(`/use-cases/${id}`);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(newStatus: UseCaseStatus) {
    setError("");
    try {
      const updated = await api.patch<UseCase>(`/use-cases/${id}`, { status: newStatus });
      setUc(updated);
    } catch (e: any) {
      setError(e.message);
    }
  }

  async function handleArchive() {
    setError("");
    try {
      await api.del(`/use-cases/${id}`);
      navigate("/");
    } catch (e: any) {
      setError(e.message);
    }
  }

  if (loading) return <p className="text-gray-500">Laden...</p>;
  if (!uc) return <div className="bg-red-50 text-red-700 px-4 py-2 rounded-md text-sm">{error}</div>;

  const allowedNext = ALLOWED_TRANSITIONS[uc.status] || [];

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Link to={`/use-cases/${id}`} className="text-sm text-blue-600 hover:text-blue-800">
          &larr; Zurück zur Ansicht
        </Link>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Use Case bearbeiten</h1>

        {error && (
          <div className="bg-red-50 text-red-700 px-4 py-2 rounded-md mb-4 text-sm">{error}</div>
        )}

        {/* Status Section (UC4) */}
        <div className="mb-6 pb-6 border-b border-gray-200">
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
            Status
          </label>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-700 font-medium">
              {STATUS_CONFIG[uc.status].label}
            </span>
            {allowedNext.length > 0 && (
              <>
                <span className="text-gray-400">&rarr;</span>
                {allowedNext.map((s) => (
                  <button
                    key={s}
                    onClick={() => handleStatusChange(s)}
                    className="px-3 py-1 text-sm rounded-md border border-gray-300 hover:bg-gray-50 transition-colors"
                  >
                    {STATUS_CONFIG[s].label}
                  </button>
                ))}
              </>
            )}
            {uc.status !== "archived" && (
              <button
                onClick={handleArchive}
                className="ml-auto px-3 py-1 text-sm rounded-md border border-red-300 text-red-600 hover:bg-red-50 transition-colors"
              >
                Archivieren
              </button>
            )}
          </div>
        </div>

        {/* Edit Fields (UC3) */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Titel</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Beschreibung</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Erwarteter Nutzen</label>
            <textarea
              value={expectedBenefit}
              onChange={(e) => setExpectedBenefit(e.target.value)}
              rows={3}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={handleSave}
            disabled={saving || !title.trim() || !description.trim()}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-40 transition-colors"
          >
            {saving ? "Speichern..." : "Speichern"}
          </button>
          <Link
            to={`/use-cases/${id}`}
            className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            Abbrechen
          </Link>
        </div>
      </div>
    </div>
  );
}
