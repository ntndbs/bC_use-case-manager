import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import UseCaseListPage from "./pages/UseCaseListPage";
import UseCaseDetailPage from "./pages/UseCaseDetailPage";
import UploadPage from "./pages/UploadPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<UseCaseListPage />} />
          <Route path="/use-cases/:id" element={<UseCaseDetailPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
