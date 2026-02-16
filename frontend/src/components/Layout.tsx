import { useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import ChatPanel from "./ChatPanel";

const NAV_ITEMS = [
  { to: "/", label: "Use Cases" },
  { to: "/upload", label: "Upload" },
];

export default function Layout() {
  const location = useLocation();
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-8">
          <Link to="/" className="text-lg font-bold text-gray-900">
            BadenCampus UCM
          </Link>
          <div className="flex gap-4">
            {NAV_ITEMS.map((item) => (
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
          <button
            onClick={() => setChatOpen(true)}
            className="ml-auto text-sm px-3 py-1.5 rounded-md border border-gray-300 text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
          >
            KI-Chat
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-6">
        <Outlet />
      </main>

      <ChatPanel open={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
  );
}
