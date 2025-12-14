import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import Classes from "../pages/Classes";
import Reservations from "../pages/Reservations";
import Navbar from "../components/Navbar";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/classes" element={<Classes />} />
        <Route path="/reservations" element={<Reservations />} />
      </Routes>
    </BrowserRouter>
  );
}
