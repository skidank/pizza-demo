import { Routes, Route } from "react-router-dom";
import MenuPage from "./pages/MenuPage";
import AdminPage from "./pages/AdminPage";
import OrderConfirmation from "./pages/OrderConfirmation";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MenuPage />} />
      <Route path="/order-confirmed" element={<OrderConfirmation />} />
      <Route path="/admin" element={<AdminPage />} />
    </Routes>
  );
}
