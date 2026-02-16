import { useEffect, useRef, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { Company } from "../api/types";
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
  const [companyId, setCompanyId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<UploadResult | null>(null);

  useEffect(() => {
    api.get<Company[]>("/companies/").then(setCompanies).catch(() => {});
  }, []);

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
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Bitte wählen...</option>
              {companies.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

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
