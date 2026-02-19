import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import type { UseCaseListResponse, Company, Industry } from "../api/types";
import StatusBadge, { STATUS_CONFIG } from "../components/StatusBadge";
import StarRating from "../components/StarRating";
import { useRefresh } from "../context/RefreshContext";
import { useAuth } from "../context/AuthContext";

export default function UseCaseListPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { refreshKey, triggerRefresh } = useRefresh();
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const [data, setData] = useState<UseCaseListResponse | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchInput, setSearchInput] = useState(searchParams.get("search") || "");
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(null);

  // Filter state from URL params
  const search = searchParams.get("search") || "";
  const status = searchParams.get("status") || "";
  const companyId = searchParams.get("company_id") || "";
  const industryId = searchParams.get("industry_id") || "";
  const page = Number(searchParams.get("page") || "1");

  function setFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    if (key !== "page") next.delete("page"); // reset page on filter change
    setSearchParams(next);
  }

  useEffect(() => {
    api.get<Company[]>("/companies/").then(setCompanies).catch((e) => console.warn("Failed to load companies:", e));
    api.get<Industry[]>("/industries/").then(setIndustries).catch((e) => console.warn("Failed to load industries:", e));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError("");

    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (status) params.set("status", status);
    if (companyId) params.set("company_id", companyId);
    if (industryId) params.set("industry_id", industryId);
    params.set("page", String(page));

    api
      .get<UseCaseListResponse>(`/use-cases/?${params}`)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [search, status, companyId, industryId, page, refreshKey]);

  async function handlePermanentDelete(e: React.MouseEvent, ucId: number) {
    e.stopPropagation();
    if (!window.confirm("Use Case endgültig löschen? Diese Aktion kann nicht rückgängig gemacht werden.")) return;
    try {
      await api.del(`/use-cases/${ucId}/permanent`);
      triggerRefresh();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Use Cases</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          placeholder="Suche..."
          value={searchInput}
          onChange={(e) => {
            const val = e.target.value;
            setSearchInput(val);
            if (debounceRef.current) clearTimeout(debounceRef.current);
            debounceRef.current = setTimeout(() => setFilter("search", val), 300);
          }}
          className="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={status}
          onChange={(e) => setFilter("status", e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Alle Status</option>
          {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
            <option key={key} value={key}>
              {cfg.label}
            </option>
          ))}
        </select>
        <select
          value={companyId}
          onChange={(e) => setFilter("company_id", e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Alle Unternehmen</option>
          {companies.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <select
          value={industryId}
          onChange={(e) => setFilter("industry_id", e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Alle Branchen</option>
          {industries.map((ind) => (
            <option key={ind.id} value={ind.id}>
              {ind.name}
            </option>
          ))}
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded-md mb-4 text-sm">
          {error}
        </div>
      )}

      {/* Table */}
      {loading ? (
        <p className="text-gray-500">Laden...</p>
      ) : data && data.data.length > 0 ? (
        <>
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <table className="w-full text-sm table-fixed">
              <thead className="bg-gray-50 text-gray-600 text-left">
                <tr>
                  <th className="px-4 py-3 font-medium w-16">ID</th>
                  <th className="px-4 py-3 font-medium">Titel</th>
                  <th className="px-4 py-3 font-medium w-32">Status</th>
                  <th className="px-4 py-3 font-medium w-48">Unternehmen</th>
                  <th className="px-4 py-3 font-medium w-40">Bewertung</th>
                  <th className="px-4 py-3 font-medium w-28">Erstellt</th>
                  {isAdmin && <th className="px-4 py-3 font-medium w-10"></th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.data.map((uc) => (
                  <tr
                    key={uc.id}
                    onClick={() => navigate(`/use-cases/${uc.id}`)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 text-gray-500">#{uc.id}</td>
                    <td className="px-4 py-3 font-medium text-gray-900">{uc.title}</td>
                    <td className="px-4 py-3">
                      <StatusBadge status={uc.status} />
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {companies.find((c) => c.id === uc.company_id)?.name || `#${uc.company_id}`}
                    </td>
                    <td className="px-4 py-3">
                      {uc.rating_average != null ? (
                        <div className="flex items-center gap-1.5">
                          <StarRating value={Math.round(uc.rating_average)} readonly />
                          <span className="text-xs text-gray-500">{uc.rating_average.toFixed(1)}</span>
                        </div>
                      ) : (
                        <span className="text-gray-400">–</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {new Date(uc.created_at).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" })}
                    </td>
                    {isAdmin && (
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={(e) => handlePermanentDelete(e, uc.id)}
                          className="text-gray-400 hover:text-red-600 transition-colors"
                          title="Endgültig löschen"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data.total > data.per_page && (
            <div className="flex items-center gap-2 mt-4 text-sm">
              <button
                disabled={page <= 1}
                onClick={() => setFilter("page", String(page - 1))}
                className="px-3 py-1 rounded border border-gray-300 disabled:opacity-40"
              >
                Zurück
              </button>
              <span className="text-gray-600">
                Seite {page} von {Math.ceil(data.total / data.per_page)}
              </span>
              <button
                disabled={page >= Math.ceil(data.total / data.per_page)}
                onClick={() => setFilter("page", String(page + 1))}
                className="px-3 py-1 rounded border border-gray-300 disabled:opacity-40"
              >
                Weiter
              </button>
            </div>
          )}
        </>
      ) : (
        <p className="text-gray-500">Keine Use Cases gefunden.</p>
      )}
    </div>
  );
}
