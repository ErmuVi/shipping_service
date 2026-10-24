import { Link, Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { NewParcelPage } from "./pages/NewParcelPage";
import { ParcelDetailPage } from "./pages/ParcelDetailPage";
import { ParcelsPage } from "./pages/ParcelsPage";
import { SupportPage } from "./pages/SupportPage";

function NotFoundPage() {
  return (
    <div className="card mx-auto max-w-md p-8 text-center">
      <p className="text-4xl">🧭</p>
      <h1 className="mt-3 text-lg font-semibold text-slate-900">
        Страница не найдена
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Проверьте адрес или вернитесь к списку посылок.
      </p>
      <Link to="/parcels" className="btn-primary mt-5">
        К посылкам
      </Link>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/parcels" replace />} />
        <Route path="parcels" element={<ParcelsPage />} />
        <Route path="parcels/new" element={<NewParcelPage />} />
        <Route path="parcels/:parcelId" element={<ParcelDetailPage />} />
        <Route path="support" element={<SupportPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
