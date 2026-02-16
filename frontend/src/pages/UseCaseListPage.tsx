import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import type { UseCaseListResponse, UseCaseStatus, Company } from "../api/types";
import StatusBadge, { STATUS_CONFIG } from "../components/StatusBadge";

export default function UseCaseListPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [data, setData] = useState<UseCaseListResponse | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Filter state from URL params
  const search = searchParams.get("search") || "";
  const status = searchParams.get("status") || "";
  const companyId = searchParams.get("company_id") || "";
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
    api.get<Company[]>("/companies/").then(setCompanies).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setError("");

    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (status) params.set("status", status);
    if (companyId) params.set("company_id", companyId);
    params.set("page", String(page));

    api
      .get<UseCaseListResponse>(`/use-cases/?${params}`)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [search, status, companyId, page]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Use Cases</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          placeholder="Suche..."
          value={search}
          onChange={(e) => setFilter("search", e.target.value)}
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
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-600 text-left">
                <tr>
                  <th className="px-4 py-3 font-medium">ID</th>
                  <th className="px-4 py-3 font-medium">Titel</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Company</th>
                  <th className="px-4 py-3 font-medium">Erstellt</th>
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
                    <td className="px-4 py-3 text-gray-500">
                      {new Date(uc.created_at).toLocaleDateString("de-DE")}
                    </td>
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
