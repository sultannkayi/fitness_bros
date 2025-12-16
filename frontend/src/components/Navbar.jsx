import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import "./Navbar.css";

export default function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // localStorage'dan token kontrolü
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);

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
          <a href="/#contact-section" className="nav-link">
            Bize Ulaşın
          </a>
          {isLoggedIn ? (
            <Link to="/profile" className="nav-link auth-link">
              Hesabım
            </Link>
          ) : (
            <Link to="/auth" className="nav-link auth-link">
              Giriş Yap
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
