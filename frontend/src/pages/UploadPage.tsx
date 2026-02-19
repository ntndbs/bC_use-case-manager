import { useEffect, useRef, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { Company, Industry } from "../api/types";
import { useAuth } from "../context/AuthContext";

interface UploadResult {
  id: number;
  filename: string;
  use_cases: { id: number; title: string; status: string }[];
}

export default function UploadPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const fileRef = useRef<HTMLInputElement>(null);

  if (user && user.role === "reader") {
    return <Navigate to="/" replace />;
  }

  const [companies, setCompanies] = useState<Company[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [companyId, setCompanyId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<UploadResult | null>(null);

  // New company form
  const [showNewCompany, setShowNewCompany] = useState(false);
  const [newCompanyName, setNewCompanyName] = useState("");
  const [selectedIndustryId, setSelectedIndustryId] = useState("");
  const [showNewIndustry, setShowNewIndustry] = useState(false);
  const [newIndustryName, setNewIndustryName] = useState("");
  const [newIndustryDesc, setNewIndustryDesc] = useState("");
  const [creating, setCreating] = useState(false);

  function loadCompanies() {
    api.get<Company[]>("/companies/").then(setCompanies).catch((e) => console.warn("Failed to load companies:", e));
  }

  useEffect(() => {
    loadCompanies();
    api.get<Industry[]>("/industries/").then(setIndustries).catch((e) => console.warn("Failed to load industries:", e));
  }, []);

  function handleCompanySelect(value: string) {
    if (value === "__new__") {
      setShowNewCompany(true);
      setCompanyId("");
    } else {
      setShowNewCompany(false);
      setCompanyId(value);
    }
  }

  function handleIndustrySelect(value: string) {
    if (value === "__new__") {
      setShowNewIndustry(true);
      setSelectedIndustryId("");
    } else {
      setShowNewIndustry(false);
      setSelectedIndustryId(value);
    }
  }

  async function handleCreateCompany() {
    setError("");
    setCreating(true);
    try {
      let industryId = selectedIndustryId;

      // Create new industry first if needed
      if (showNewIndustry && newIndustryName.trim()) {
        const ind = await api.post<{ id: number; name: string }>("/industries/", {
          name: newIndustryName.trim(),
          description: newIndustryDesc.trim() || null,
        });
        industryId = String(ind.id);
        setIndustries((prev) => [...prev, { id: ind.id, name: ind.name, description: newIndustryDesc.trim() || null }]);
        setShowNewIndustry(false);
        setNewIndustryName("");
        setNewIndustryDesc("");
      }

      if (!industryId) {
        setError("Bitte eine Branche auswählen oder anlegen.");
        return;
      }

      // Create company
      const comp = await api.post<{ id: number; name: string; industry_id: number }>("/companies/", {
        name: newCompanyName.trim(),
        industry_id: Number(industryId),
      });

      setCompanies((prev) => [...prev, { id: comp.id, name: comp.name, industry_id: comp.industry_id }]);
      setCompanyId(String(comp.id));
      setShowNewCompany(false);
      setNewCompanyName("");
      setSelectedIndustryId("");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setCreating(false);
    }
  }

  async function handleUpload() {
    if (!file || !companyId) return;

    setUploading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("company_id", companyId);

    try {
      const data = await api.upload<UploadResult>("/transcripts/", formData);
      setResult(data);
      setFile(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Transkript Upload</h1>

      <div className="bg-white rounded-lg border border-gray-200 p-6 max-w-lg">
        {error && (
          <div className="bg-red-50 text-red-700 px-4 py-2 rounded-md mb-4 text-sm">{error}</div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Unternehmen</label>
            <select
              value={showNewCompany ? "__new__" : companyId}
              onChange={(e) => handleCompanySelect(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Bitte wählen...</option>
              {companies.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
              <option value="__new__">+ Neue Firma</option>
            </select>
          </div>

          {/* Inline: New Company Form */}
          {showNewCompany && (
            <div className="border border-blue-200 bg-blue-50 rounded-md p-4 space-y-3">
              <p className="text-sm font-medium text-blue-800">Neue Firma anlegen</p>

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Firmenname</label>
                <input
                  type="text"
                  value={newCompanyName}
                  onChange={(e) => setNewCompanyName(e.target.value)}
                  placeholder="z.B. Stadtwerke Beispielstadt GmbH"
                  className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Branche</label>
                <select
                  value={showNewIndustry ? "__new__" : selectedIndustryId}
                  onChange={(e) => handleIndustrySelect(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Bitte wählen...</option>
                  {industries.map((i) => (
                    <option key={i.id} value={i.id}>{i.name}</option>
                  ))}
                  <option value="__new__">+ Neue Branche</option>
                </select>
              </div>

              {/* Inline: New Industry Form */}
              {showNewIndustry && (
                <div className="border border-green-200 bg-green-50 rounded-md p-3 space-y-2">
                  <p className="text-xs font-medium text-green-800">Neue Branche anlegen</p>
                  <input
                    type="text"
                    value={newIndustryName}
                    onChange={(e) => setNewIndustryName(e.target.value)}
                    placeholder="Branchenname"
                    className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    value={newIndustryDesc}
                    onChange={(e) => setNewIndustryDesc(e.target.value)}
                    placeholder="Beschreibung (optional)"
                    className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              <button
                onClick={handleCreateCompany}
                disabled={creating || !newCompanyName.trim() || (!selectedIndustryId && !(showNewIndustry && newIndustryName.trim()))}
                className="w-full px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-40 transition-colors"
              >
                {creating ? "Wird angelegt..." : "Firma anlegen"}
              </button>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Transkript-Datei (.txt)
            </label>
            <input
              ref={fileRef}
              type="file"
              accept=".txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          <button
            onClick={handleUpload}
            disabled={uploading || !file || !companyId}
            className="w-full px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-40 transition-colors"
          >
            {uploading ? "Wird hochgeladen & analysiert..." : "Hochladen & Use Cases extrahieren"}
          </button>
        </div>

        {/* Result */}
        {result && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h2 className="text-sm font-medium text-gray-900 mb-2">
              Transkript #{result.id} hochgeladen
            </h2>
            {result.use_cases.length > 0 ? (
              <>
                <p className="text-sm text-green-700 mb-3">
                  {result.use_cases.length} Use Case(s) extrahiert:
                </p>
                <ul className="space-y-1">
                  {result.use_cases.map((uc) => (
                    <li key={uc.id}>
                      <button
                        onClick={() => navigate(`/use-cases/${uc.id}`)}
                        className="text-sm text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        #{uc.id} — {uc.title}
                      </button>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p className="text-sm text-yellow-700">
                Keine Use Cases extrahiert. Versuche es erneut über den Chat.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
