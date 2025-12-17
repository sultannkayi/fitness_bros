import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Profile.css";

export default function Profile() {
  const navigate = useNavigate();
  
  const [userData, setUserData] = useState({
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

  const [reservations, setReservations] = useState([]);

  useEffect(() => {
    // localStorage'dan kullanıcı bilgilerini çek
    const storedUserData = localStorage.getItem('userData');
    if (storedUserData) {
      const parsedData = JSON.parse(storedUserData);
      setUserData({
        name: parsedData.name,
        gender: parsedData.gender,
        dateOfBirth: parsedData.dateOfBirth,
        height: parsedData.height,
        weight: parsedData.weight,
        age: parsedData.age,
        stats: {
          weight: parsedData.weight,
          height: parsedData.height,
          age: parsedData.age
        }
      });
    }

    // Rezervasyonları çek
    const storedReservations = localStorage.getItem('reservations');
    if (storedReservations) {
      setReservations(JSON.parse(storedReservations));
    }
  }, []);

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
              <p className="list-label">Rezervasyonlarım</p>
              
              {reservations.length > 0 ? (
                <div className="reservations-list">
                  {reservations.map((reservation) => (
                    <div key={reservation.id} className="reservation-item">
                      <div className="reservation-header">
                        <h4 className="reservation-class-name">{reservation.className}</h4>
                        <span className={`reservation-status ${reservation.status === 'Onaylandı' ? 'confirmed' : ''}`}>
                          {reservation.status}
                        </span>
                      </div>
                      <p className="reservation-instructor">👤 Eğitmen: {reservation.instructor}</p>
                      <div className="reservation-details">
                        <span className="reservation-day">📅 {reservation.day}</span>
                        <span className="reservation-time">🕐 {reservation.time}</span>
                      </div>
                      <p className="reservation-date">Rezervasyon Tarihi: {reservation.date}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-reservations">
                  <p>Henüz rezervasyonunuz bulunmamaktadır.</p>
                  <button className="go-to-reservations" onClick={() => navigate('/reservations')}>
                    Rezervasyon Yap
                  </button>
                </div>
              )}
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
