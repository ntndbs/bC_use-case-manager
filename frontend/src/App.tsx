import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { RefreshProvider } from "./context/RefreshContext";
import LoginPage from "./pages/LoginPage";
import UseCaseListPage from "./pages/UseCaseListPage";
import UseCaseDetailPage from "./pages/UseCaseDetailPage";
import UseCaseEditPage from "./pages/UseCaseEditPage";
import UploadPage from "./pages/UploadPage";
import RegisterPage from "./pages/RegisterPage";

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-500">Laden...</div>;
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <RefreshProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<UseCaseListPage />} />
          <Route path="/use-cases/:id" element={<UseCaseDetailPage />} />
          <Route path="/use-cases/:id/edit" element={<UseCaseEditPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Route>
        <Route path="/login" element={<Navigate to="/" replace />} />
      </Routes>
    </RefreshProvider>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
