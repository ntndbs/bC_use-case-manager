import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";

interface UserEntry {
  id: number;
  email: string;
  role: "reader" | "maintainer" | "admin";
  is_active: boolean;
  created_at: string;
}

const ROLE_OPTIONS = [
  { value: "reader", label: "Reader" },
  { value: "maintainer", label: "Maintainer" },
  { value: "admin", label: "Admin" },
];

export default function UserManagementPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<UserEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  if (user && user.role !== "admin") {
    return <Navigate to="/" replace />;
  }

  useEffect(() => {
    api
      .get<UserEntry[]>("/auth/users")
      .then(setUsers)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(userId: number) {
    if (!window.confirm("Benutzer endgültig löschen? Diese Aktion kann nicht rückgängig gemacht werden.")) return;
    setError("");
    try {
      await api.del(`/auth/users/${userId}`);
      setUsers((u) => u.filter((x) => x.id !== userId));
    } catch (e: any) {
      setError(e.message);
    }
  }

  async function handleRoleChange(userId: number, newRole: string) {
    setError("");
    const prev = users;
    // Optimistic update
    setUsers((u) => u.map((x) => (x.id === userId ? { ...x, role: newRole as UserEntry["role"] } : x)));
    try {
      await api.patch<UserEntry>(`/auth/users/${userId}`, { role: newRole });
    } catch (e: any) {
      setError(e.message);
      setUsers(prev); // Rollback
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Benutzerverwaltung</h1>

      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded-md mb-4 text-sm">{error}</div>
      )}

      {loading ? (
        <p className="text-gray-500">Laden...</p>
      ) : users.length > 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">E-Mail</th>
                <th className="px-4 py-3 font-medium">Rolle</th>
                <th className="px-4 py-3 font-medium">Registriert</th>
                <th className="px-4 py-3 font-medium w-10"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-900">
                    {u.email}
                    {u.id === user?.id && (
                      <span className="ml-2 text-xs text-gray-400">(Du)</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      disabled={u.id === user?.id}
                      className="border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      {ROLE_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(u.created_at).toLocaleDateString("de-DE")}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {u.id !== user?.id && (
                      <button
                        onClick={() => handleDelete(u.id)}
                        className="text-gray-400 hover:text-red-600 transition-colors"
                        title="Benutzer löschen"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-gray-500">Keine Benutzer gefunden.</p>
      )}
    </div>
  );
}
