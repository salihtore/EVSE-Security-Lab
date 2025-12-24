import { Routes, Route } from "react-router-dom";
import MainLayout from "./layout/MainLayout";

export default function App() {
  return (
    <Routes>
      <Route path="/*" element={<MainLayout />} />
    </Routes>
  );
}
