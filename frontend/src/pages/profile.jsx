import { useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Profile.css";

const PLAN_TYPES = [
  {
    id: 'baslangic',
    name: 'Başlangıç Paketi',
    price: '₺999/ay',
    features: ['Temel Dersler', 'Haftalık 3 Ders', 'Soyunma Odası Erişimi']
  },
  {
    id: 'premium',
    name: 'Premium Paket',
    price: '₺1499/ay',
    features: ['Tüm Dersler', 'Sınırsız Rezervasyon', 'Kişisel Dolap', 'Sauna']
  },
  {
    id: 'ultimate',
    name: 'Ultimate Paket',
    price: '₺1999/ay',
    features: ['VIP Erişim', 'Özel Antrenör', 'Beslenme Programı', 'Spa & Masaj']
  },
];

export default function Profile() {
  const navigate = useNavigate();
  const location = useLocation();
  const [userData, setUserData] = useState(null);
  const [reservations, setReservations] = useState([]);
  const [fitnessClasses, setFitnessClasses] = useState([]);
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  const loadData = useCallback(() => {
    const token = localStorage.getItem("token");
    const storedUserData = localStorage.getItem("userData");
    if (!token || !storedUserData) {
      navigate("/auth");
      return;
    }
    const parsedData = JSON.parse(storedUserData);
    setUserData(parsedData);

    const storedReservations = localStorage.getItem("reservations");
    if (storedReservations) {
      setReservations(JSON.parse(storedReservations));
    } else {
      setReservations([]);
    }

    const storedClasses = JSON.parse(localStorage.getItem("fitnessClasses")) || [];
    setFitnessClasses(storedClasses);
  }, [navigate]);

  useEffect(() => {
    loadData();
  }, [location, loadData]);

  useEffect(() => {
    const handleFocus = () => {
      loadData();
    };

    const handleStorageChange = (e) => {
      if (e.key === "reservations" || e.key === "fitnessClasses") {
        loadData();
      }
    };

    window.addEventListener("focus", handleFocus);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("focus", handleFocus);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [loadData]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/auth");
  };

  const handlePlanUpdate = () => {
    if (!selectedPlan) return;

    const confirmed = window.confirm(`${selectedPlan.name} (${selectedPlan.price}) paketine geçmek istediğinize emin misiniz?`);
    if (!confirmed) return;

    const updatedUserData = {
      ...userData,
      membership_type: selectedPlan.id,
      membership_name: selectedPlan.name,
      membership_price: selectedPlan.price
    };

    localStorage.setItem("userData", JSON.stringify(updatedUserData));
    setUserData(updatedUserData);
    setShowPlanModal(false);
    setSelectedPlan(null);
    alert("Üyelik planınız başarıyla güncellendi!");
  };

  const handleCancelReservation = (id) => {
    const confirmCancel = window.confirm("Rezervasyonunuzu iptal etmek istediğinize emin misiniz?");
    if (!confirmCancel) return;

    const reservationToCancel = reservations.find((r) => r.id === id);
    if (!reservationToCancel) return;

    const updatedReservations = reservations.filter((reservation) => reservation.id !== id);
    setReservations(updatedReservations);
    localStorage.setItem("reservations", JSON.stringify(updatedReservations));

    const updatedClasses = fitnessClasses.map((cls) => {
      if (cls.name !== reservationToCancel.className) return cls;
      return {
        ...cls,
        schedule: cls.schedule.map((sch) =>
          sch.day === reservationToCancel.day && sch.time === reservationToCancel.time
            ? { ...sch, available: sch.available + 1 }
            : sch
        ),
      };
    });

    setFitnessClasses(updatedClasses);
    localStorage.setItem("fitnessClasses", JSON.stringify(updatedClasses));
  };

  const getCurrentPlanInfo = () => {
    if (!userData.membership_type) return "Plan Seçilmedi";
    const plan = PLAN_TYPES.find(p => p.id === userData.membership_type);
    return plan ? `${plan.name}` : "Plan Seçilmedi";
  };

  if (!userData) return null;

  return (
    <div className="profile-page">
      <div className="profile-container">
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
                {userData.gender === "Male" ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="100"
                    height="100"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <circle cx="12" cy="8" r="5" />
                    <path d="M3 21v-2a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v2" />
                  </svg>
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="100"
                    height="100"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <circle cx="12" cy="8" r="5" />
                    <path d="M3 21v-2a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v2" />
                    <path d="M12 13v-2" />
                  </svg>
                )}
              </div>
              <h2 className="profile-name">{userData.name}</h2>
              <p className="profile-age">{userData.age}</p>
              <button className="profile-plan-button" onClick={() => setShowPlanModal(true)}>
                {getCurrentPlanInfo()}
              </button>
            </div>
            <div className="profile-stats">
              <div className="stat-item">
                <div className="stat-icon weight-icon">⚖️</div>
                <span className="stat-value">{userData.weight}</span>
              </div>
              <div className="stat-item">
                <div className="stat-icon height-icon">📏</div>
                <span className="stat-value">{userData.height}</span>
              </div>
              <div className="stat-item">
                <div className="stat-icon age-icon">⚡</div>
                <span className="stat-value">{userData.age}</span>
              </div>
            </div>
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
              <button
                className="go-to-reservations"
                onClick={() => navigate("/reservations")}
              >
                Rezervasyon Yap
              </button>
              {reservations.length > 0 ? (
                <div className="reservations-list">
                  {reservations.map((r) => (
                    <div key={r.id} className="reservation-item">
                      <div className="reservation-header">
                        <h4 className="reservation-class-name">{r.className}</h4>
                        <span className="reservation-status confirmed">
                          {r.status}
                        </span>
                      </div>
                      <p className="reservation-instructor">
                        👤 Eğitmen: {r.instructor}
                      </p>
                      <div className="reservation-details">
                        <span>📅 {r.day}</span>
                        <span>🕐 {r.time}</span>
                      </div>
                      <button
                        className="cancel-reservation-button"
                        onClick={() => handleCancelReservation(r.id)}
                      >
                        İptal Et
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-reservations">
                  <p>Henüz rezervasyonunuz bulunmamaktadır.</p>
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="profile-right">
          <div className="gym-image">
            <img
              src="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&h=800&fit=crop"
              alt="Gym"
            />
            <div className="gym-overlay">
              <h3 className="gym-text">
                FOCUS<br />ON YOUR<br />GOALS
              </h3>
              <p className="gym-subtext">
                THEN WORK<br />FOR IT
              </p>
            </div>
          </div>
        </div>
      </div>

      {showPlanModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div style={{
            backgroundColor: '#1a1a1a',
            padding: '40px',
            borderRadius: '20px',
            maxWidth: '600px',
            width: '100%',
            border: '2px solid #333',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)'
          }}>
            <h2 style={{
              color: '#fff',
              marginBottom: '30px',
              textAlign: 'center',
              fontSize: '28px',
              fontWeight: 'bold'
            }}>
              Üyelik Paketini Seçin
            </h2>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '15px',
              marginBottom: '30px'
            }}>
              {PLAN_TYPES.map((plan) => (
                <div
                  key={plan.id}
                  onClick={() => setSelectedPlan(plan)}
                  style={{
                    padding: '20px',
                    borderRadius: '12px',
                    border: selectedPlan?.id === plan.id ? '3px solid #ff4d00' : '2px solid #444',
                    cursor: 'pointer',
                    backgroundColor: selectedPlan?.id === plan.id ? '#2a2a2a' : '#1f1f1f',
                    transition: 'all 0.3s ease',
                    transform: selectedPlan?.id === plan.id ? 'scale(1.02)' : 'scale(1)',
                    boxShadow: selectedPlan?.id === plan.id ? '0 8px 20px rgba(255, 77, 0, 0.3)' : 'none'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '15px'
                  }}>
                    <div>
                      <h3 style={{
                        color: '#fff',
                        margin: '0 0 8px 0',
                        fontSize: '22px',
                        fontWeight: 'bold'
                      }}>
                        {plan.name}
                      </h3>
                      <div style={{
                        color: '#ff4d00',
                        fontWeight: 'bold',
                        fontSize: '20px'
                      }}>
                        {plan.price}
                      </div>
                    </div>
                    <div style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      border: selectedPlan?.id === plan.id ? '2px solid #ff4d00' : '2px solid #666',
                      backgroundColor: selectedPlan?.id === plan.id ? '#ff4d00' : 'transparent',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      {selectedPlan?.id === plan.id && (
                        <div style={{
                          width: '10px',
                          height: '10px',
                          borderRadius: '50%',
                          backgroundColor: '#fff'
                        }} />
                      )}
                    </div>
                  </div>
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px'
                  }}>
                    {plan.features.map((feature, idx) => (
                      <div key={idx} style={{
                        color: '#aaa',
                        fontSize: '14px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}>
                        <span style={{ color: '#ff4d00' }}>✓</span>
                        {feature}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div style={{
              display: 'flex',
              gap: '15px',
              justifyContent: 'flex-end'
            }}>
              <button
                onClick={() => {
                  setShowPlanModal(false);
                  setSelectedPlan(null);
                }}
                style={{
                  padding: '12px 30px',
                  background: 'transparent',
                  border: '2px solid #666',
                  color: '#fff',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: '600',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.borderColor = '#888';
                  e.target.style.backgroundColor = '#2a2a2a';
                }}
                onMouseLeave={(e) => {
                  e.target.style.borderColor = '#666';
                  e.target.style.backgroundColor = 'transparent';
                }}
              >
                İptal
              </button>
              <button
                onClick={handlePlanUpdate}
                disabled={!selectedPlan}
                style={{
                  padding: '12px 30px',
                  background: selectedPlan ? 'linear-gradient(135deg, #ff4d00 0%, #ff6b00 100%)' : '#555',
                  border: 'none',
                  color: '#fff',
                  borderRadius: '8px',
                  cursor: selectedPlan ? 'pointer' : 'not-allowed',
                  fontSize: '16px',
                  fontWeight: '600',
                  transition: 'all 0.3s ease',
                  boxShadow: selectedPlan ? '0 4px 15px rgba(255, 77, 0, 0.4)' : 'none'
                }}
                onMouseEnter={(e) => {
                  if (selectedPlan) {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 20px rgba(255, 77, 0, 0.5)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = selectedPlan ? '0 4px 15px rgba(255, 77, 0, 0.4)' : 'none';
                }}
              >
                Planı Onayla
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}