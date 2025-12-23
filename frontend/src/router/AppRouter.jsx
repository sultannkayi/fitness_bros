import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import Classes from "../pages/Classes";
import Reservations from "../pages/Reservations";
import Profile from "../pages/profile";
import Auth from "../pages/Auth";
import Navbar from "../components/Navbar";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/classes" element={<Classes />} />
        <Route path="/reservations" element={<Reservations />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="*" element={<Auth />} /> {/* Yanlış yollar auth'a düşsün */}
      </Routes>
    </BrowserRouter>
  );
}