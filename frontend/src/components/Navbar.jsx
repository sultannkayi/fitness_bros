import { Link } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          Fitness <span className="brand-highlight">BROS</span>
        </Link>
        
        <div className="navbar-links">
          <a href="/#classes-section" className="nav-link">
            Sınıflarımız
          </a>
          <a href="/#about-section" className="nav-link">
            Hakkımızda
          </a>
          <Link to="/reservations" className="nav-link">
            Bize Ulaşın
          </Link>
          <Link to="/profile" className="nav-link auth-link">
            Hesabım
          </Link>
        </div>
      </div>
    </nav>
  );
}
