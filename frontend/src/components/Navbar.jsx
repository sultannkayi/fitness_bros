import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import "./Navbar.css";

export default function Navbar() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
  }, []);

  const handleProfileClick = (e) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');

    if (token) {
      navigate("/profile");
    } else {
      navigate("/auth");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsLoggedIn(false);
    navigate("/auth");
  };

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
            Üyelik Planlarımız
          </a>

          {/* Profile ikonu */}
          <div 
            className="nav-link auth-link" 
            onClick={handleProfileClick}
            style={{ cursor: "pointer" }}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="24" 
              height="24" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>

          {/* İstersen girişliyken Çıkış butonu göster */}
          {isLoggedIn && (
            <button onClick={handleLogout} className="nav-link logout-btn">
              Çıkış Yap
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}