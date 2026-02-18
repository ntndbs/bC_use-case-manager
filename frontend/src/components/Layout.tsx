import { useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ChatPanel from "./ChatPanel";

const ROLE_LEVEL: Record<string, number> = { reader: 0, maintainer: 1, admin: 2 };

const NAV_ITEMS = [
  { to: "/", label: "Use Cases" },
  { to: "/upload", label: "Upload", minRole: "maintainer" },
  { to: "/users", label: "User", minRole: "admin" },
];

export default function Layout() {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-8">
          <Link to="/" className="text-lg font-bold text-gray-900">
            BadenCampus UCM
          </Link>
          <div className="flex gap-4">
            {NAV_ITEMS.filter(
              (item) => !item.minRole || (user && ROLE_LEVEL[user.role] >= ROLE_LEVEL[item.minRole])
            ).map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className={`text-sm px-3 py-1.5 rounded-md transition-colors ${
                  location.pathname === item.to
                    ? "bg-blue-100 text-blue-700 font-medium"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
          <div className="ml-auto flex items-center gap-3">
            <button
              onClick={() => setChatOpen(true)}
              className="text-sm px-3 py-1.5 rounded-md border border-gray-300 text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
            >
              KI-Chat
            </button>
            {user && (
              <>
                <span className="text-xs text-gray-500">
                  {user.email} ({user.role})
                </span>
                <button
                  onClick={logout}
                  className="text-sm px-3 py-1.5 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
                >
                  Abmelden
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-6">
        <Outlet />
      </main>

      <ChatPanel open={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
  );
}
