import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { UseCase, Company } from "../api/types";
import StatusBadge from "../components/StatusBadge";
import StarRating from "../components/StarRating";
import { useAuth } from "../context/AuthContext";

export default function UseCaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const canEdit = user && (user.role === "maintainer" || user.role === "admin");
  const [uc, setUc] = useState<UseCase | null>(null);
  const [companyName, setCompanyName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get<UseCase>(`/use-cases/${id}`),
      api.get<Company[]>("/companies/"),
    ])
      .then(([ucData, companies]) => {
        setUc(ucData);
        setCompanyName(companies.find((c) => c.id === ucData.company_id)?.name ?? null);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleRate(field: string, value: number) {
    if (!uc) return;
    const prev = uc;
    setUc({ ...uc, [field]: value });
    try {
      const updated = await api.patch<UseCase>(`/use-cases/${uc.id}`, { [field]: value });
      setUc(updated);
    } catch {
      setUc(prev);
    }
  }

  if (loading) return <p className="text-gray-500">Laden...</p>;
  if (error) return <div className="bg-red-50 text-red-700 px-4 py-2 rounded-md text-sm">{error}</div>;
  if (!uc) return null;

  const ratingCategories = [
    { key: "rating_effort", label: "Aufwand" },
    { key: "rating_benefit", label: "Nutzen" },
    { key: "rating_feasibility", label: "Machbarkeit" },
    { key: "rating_data_availability", label: "Datenverfügbarkeit" },
    { key: "rating_strategic_relevance", label: "Strategische Relevanz" },
  ] as const;

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Link to="/" className="text-sm text-blue-600 hover:text-blue-800">&larr; Zurück</Link>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{uc.title}</h1>
            <p className="text-sm text-gray-500 mt-1">ID #{uc.id}</p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={uc.status} />
            {canEdit && (
              <button
                onClick={() => navigate(`/use-cases/${uc.id}/edit`)}
                className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Bearbeiten
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <Field label="Beschreibung" fullWidth>
            <p className="text-gray-700 whitespace-pre-wrap">{uc.description}</p>
          </Field>

          <Field label="Erwarteter Nutzen">
            <p className="text-gray-700">{uc.expected_benefit || "—"}</p>
          </Field>

          <Field label="Stakeholder">
            {uc.stakeholders && uc.stakeholders.length > 0 ? (
              <ul className="space-y-1">
                {uc.stakeholders.map((s, i) => (
                  <li key={i} className="text-gray-700">
                    <span className="font-medium">{s.name}</span>
                    {s.role && <span className="text-gray-500"> — {s.role}</span>}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-400">Keine Stakeholder</p>
            )}
          </Field>

          <Field label="Unternehmen">
            <p className="text-gray-700">{companyName ? `${companyName} (ID #${uc.company_id})` : `ID #${uc.company_id}`}</p>
          </Field>

          <Field label="Transkript">
            <p className="text-gray-700">{uc.transcript_id ? `ID #${uc.transcript_id}` : "—"}</p>
          </Field>

          <Field label="Erstellt am">
            <p className="text-gray-700">
              {new Date(uc.created_at).toLocaleString("de-DE")}
            </p>
          </Field>

          <Field label="Zuletzt geändert">
            <p className="text-gray-700">
              {new Date(uc.updated_at).toLocaleString("de-DE")}
            </p>
          </Field>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Bewertung</h2>
            {uc.rating_average != null && (
              <span className="text-sm font-semibold text-amber-600">
                &#8960; {uc.rating_average.toFixed(1)}
              </span>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {ratingCategories.map(({ key, label }) => (
              <div key={key} className="flex items-center justify-between gap-2">
                <span className="text-sm text-gray-700">{label}</span>
                <StarRating
                  value={uc[key]}
                  onChange={canEdit ? (v) => handleRate(key, v) : undefined}
                  readonly={!canEdit}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  children,
  fullWidth,
}: {
  label: string;
  children: React.ReactNode;
  fullWidth?: boolean;
}) {
  return (
    <div className={fullWidth ? "md:col-span-2" : ""}>
      <dt className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
        {label}
      </dt>
      <dd>{children}</dd>
    </div>
  );
}
