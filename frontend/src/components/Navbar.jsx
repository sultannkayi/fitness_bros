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
          <Link to={isLoggedIn ? "/profile" : "/auth"} className="nav-link auth-link">
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
          </Link>
        </div>
      </div>
    </nav>
  );
}
