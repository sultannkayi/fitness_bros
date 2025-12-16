import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Profile.css";

export default function Profile() {
  const navigate = useNavigate();
  
  const [userData] = useState({
    name: "Leslie Alexander",
    gender: "Male",
    dateOfBirth: "22 may 1995",
    height: "172 cm",
    weight: "62 kg",
    age: "26 years",
    stats: {
      weight: "55 kg",
      height: "167 cm",
      age: "26 years"
    }
  });

  const handleLogout = () => {
    // Logout işlemleri (localStorage temizleme vs.)
    localStorage.removeItem('token');
    // Home sayfasına yönlendir
    navigate('/');
  };

  return (
    <div className="profile-page">
      <div className="profile-container">
        {/* Left Section - User Info */}
        <div className="profile-left">
          <div className="profile-header">
            <div className="profile-header-content">
              <h1 className="profile-brand">
                Fitness <span className="brand-orange">BROSS</span>
              </h1>
              <button className="logout-button" onClick={handleLogout}>
                🚪 Çıkış Yap
              </button>
            </div>
          </div>

          <div className="profile-card">
            <div className="profile-avatar-section">
              <div className="profile-avatar">
                <img 
                  src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop" 
                  alt={userData.name}
                />
              </div>
              <h2 className="profile-name">{userData.name}</h2>
              <p className="profile-age">{userData.age.split(' ')[0]}</p>
              <button className="profile-plan-button">Planınız</button>
            </div>

            {/* Stats Section */}
            <div className="profile-stats">
              <div className="stat-item">
                <div className="stat-icon weight-icon">⚖️</div>
                <span className="stat-value">{userData.stats.weight}</span>
              </div>
              <div className="stat-item">
                <div className="stat-icon height-icon">📏</div>
                <span className="stat-value">{userData.stats.height}</span>
              </div>
              <div className="stat-item">
                <div className="stat-icon age-icon">⚡</div>
                <span className="stat-value">{userData.stats.age}</span>
              </div>
            </div>

            {/* Details Section */}
            <div className="profile-details">
              <div className="detail-row">
                <span className="detail-label">Name</span>
                <span className="detail-value">{userData.name}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Gender</span>
                <span className="detail-value">{userData.gender}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Date of birth</span>
                <span className="detail-value">{userData.dateOfBirth}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Height</span>
                <span className="detail-value">{userData.height}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Weight</span>
                <span className="detail-value">{userData.weight}</span>
              </div>
            </div>

            <div className="profile-list-section">
              <p className="list-label">Border</p>
              <p className="list-value">List</p>
              <p className="list-number">228</p>
            </div>
          </div>
        </div>

        {/* Right Section - Gym Image */}
        <div className="profile-right">
          <div className="gym-image">
            <img 
              src="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&h=800&fit=crop" 
              alt="Gym"
            />
            <div className="gym-overlay">
              <h3 className="gym-text">FOCUS<br/>ON YOUR<br/>GOALS</h3>
              <p className="gym-subtext">THEN WORK<br/>FOR IT</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
