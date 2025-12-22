import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import "./Reservations.css";
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';

const MySwal = withReactContent(Swal);

// PricingEngine mantığını frontend'de tekrar ettik (sadece gösterim için)
const MEMBERSHIP_PLANS = {
  student: { price_multiplier: 0.8, peak_multiplier: 1.2, surge_apply: true },
  standard: { price_multiplier: 1.0, peak_multiplier: 1.5, surge_apply: true },
  premium: { price_multiplier: 0.0, peak_multiplier: 1.0, surge_apply: false },
};

const PEAK_START = 18;
const PEAK_END = 22;
const SURGE_THRESHOLD = 0.8; // %80 doluluk üstü

// Kullanıcının ödeyeceği gerçek fiyatı hesapla (sadece UI için)
const calculateUserPrice = (basePrice, availableSpots, capacity, dateTime, membershipType = 'standard') => {
  if (!basePrice || !membershipType) return basePrice;

  const plan = MEMBERSHIP_PLANS[membershipType] || MEMBERSHIP_PLANS.standard;

  // Premium ücretsiz
  if (plan.price_multiplier === 0) return 0;

  let price = basePrice * plan.price_multiplier;

  // Peak hour kontrolü
  const hour = new Date(dateTime).getHours();
  const isPeak = hour >= PEAK_START && hour <= PEAK_END;
  if (isPeak) {
    price *= plan.peak_multiplier;
  }

  // Surge pricing
  const occupancyRate = capacity > 0 ? (capacity - availableSpots) / capacity : 0;
  if (plan.surge_apply && occupancyRate > SURGE_THRESHOLD) {
    const excess = occupancyRate - SURGE_THRESHOLD;
    const surgeMultiplier = 1.0 + Math.floor(excess / 0.1) * 0.1; // Her %10 için +%10
    price *= surgeMultiplier;
  }

  return Math.round(price * 100) / 100; // 2 ondalık
};

export default function Reservations() {
  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem("access_token")) {
      navigate("/auth", { replace: true });
    }
  }, [navigate]);

  const [fitnessClasses, setFitnessClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedClass, setSelectedClass] = useState(null);
  const [userMembership, setUserMembership] = useState('standard'); // Kullanıcının üyelik tipi

  // Kullanıcı profilinden üyelik tipini çek
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const res = await api.get("/memberships/me/");
        setUserMembership(res.data.membership_type || 'standard');
      } catch (err) {
        console.error("Profil bilgisi alınamadı:", err);
        setUserMembership('standard'); // fallback
      }
    };
    fetchUserData();
  }, []);

  const fetchClasses = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get("/classes/");
      setFitnessClasses(response.data);
      setError(null);
    } catch (err) {
      console.error("Dersler yüklenirken hata:", err);
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/auth");
      } else {
        setError("Dersler yüklenemedi. Lütfen daha sonra tekrar deneyin.");
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchClasses();
  }, [fetchClasses]);

  useEffect(() => {
    const handleFocus = () => fetchClasses();
    window.addEventListener("focus", handleFocus);
    return () => window.removeEventListener("focus", handleFocus);
  }, [fetchClasses]);

  const handleClassSelect = (cls) => {
    setSelectedClass(cls);
  };

  const handleReservation = async () => {
    if (!selectedClass) return;

    try {
      await api.post("/reservations/", {
        fitness_class_id: selectedClass.id,
      });

      await MySwal.fire({
        icon: 'success',
        title: 'Rezervasyon Başarılı!',
        text: 'Dersiniz başarıyla rezerve edildi.',
        confirmButtonText: 'Tamam',
        timer: 3000,
        timerProgressBar: true,
      });

      navigate("/profile");
    } catch (err) {
      console.error("Rezervasyon hatası:", err);
      const errorMessage = err.response?.data?.detail || 'Rezervasyon yapılamadı. Ders dolu veya başka bir sorun olabilir.';

      MySwal.fire({
        icon: 'error',
        title: 'Rezervasyon Hatası',
        text: errorMessage,
        confirmButtonText: 'Tamam',
      });
    }
  };

  if (loading) {
    return (
      <div className="reservations-page">
        <p>Yükleniyor...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="reservations-page">
        <p style={{ color: "red" }}>{error}</p>
        <button onClick={fetchClasses}>Tekrar Dene</button>
      </div>
    );
  }

  return (
    <div className="reservations-container">
      <div className="reservations-header">
        <h1 className="reservations-title">
          Ders <span className="highlight">Rezervasyon</span>
        </h1>
        <p className="reservations-subtitle">
          Aşağıdaki derslerden birini seçerek rezervasyon yapabilirsiniz
        </p>
      </div>

      <div className="reservations-content">
        <div className="classes-list">
          <h2 className="list-title">Mevcut Dersler</h2>
          {fitnessClasses.length === 0 ? (
            <div className="no-selection">
              <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <line x1="10" y1="9" x2="8" y2="9"></line>
              </svg>
              <h3>Henüz ders bulunmuyor</h3>
              <p>Şu anda aktif ders bulunmamaktadır. Daha sonra tekrar kontrol edin.</p>
            </div>
          ) : (
            fitnessClasses.map((cls) => {
              const userPrice = calculateUserPrice(cls.base_price, cls.available_spots, cls.capacity, cls.date_time, userMembership);

              return (
                <div
                  key={cls.id}
                  className={`class-item ${selectedClass?.id === cls.id ? "selected" : ""}`}
                  onClick={() => handleClassSelect(cls)}
                >
                  <div className="class-item-header">
                    <h3 className="class-item-name">{cls.name}</h3>
                    <span className="class-capacity">
                      {cls.available_spots}/{cls.capacity} kişi
                    </span>
                  </div>
                  <p className="class-instructor">
                    <strong>👤 Eğitmen:</strong> {cls.instructor_name}
                  </p>
                  <p className="class-instructor">
                    <strong>📅 Tarih:</strong> {new Date(cls.date_time).toLocaleString("tr-TR")}
                  </p>
                  <div className="schedule-availability">
                    <span className={`availability-badge ${cls.available_spots === 0 ? 'unavailable' : 'available'}`}>
                      {cls.available_spots === 0 ? 'DOLU' : `${cls.available_spots} BOŞ YER`}
                    </span>
                  </div>
                  <p className="class-description">
                    {userMembership === 'premium' ? (
                      <strong>ÜCRETSİZ</strong>
                    ) : (
                      <>
                        Siz ödeyeceksiniz:{' '}
                        <strong>₺{userPrice.toFixed(2)}</strong>{' '}
                        <span style={{ fontSize: '0.8em', color: '#888' }}>
                          (Normal fiyat: ₺{cls.base_price})
                        </span>
                      </>
                    )}
                  </p>
                </div>
              );
            })
          )}
        </div>

        <div className="schedule-selection">
          {!selectedClass ? (
            <div className="no-selection">
              <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <h3>Ders Seçin</h3>
              <p>Rezervasyon yapmak için soldaki listeden bir ders seçin</p>
            </div>
          ) : selectedClass.available_spots > 0 ? (
            <>
              <div className="selected-class-info">
                <h3>{selectedClass.name}</h3>
                <p>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  Eğitmen: {selectedClass.instructor_name}
                </p>
                <p>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="16" y1="2" x2="16" y2="6"></line>
                    <line x1="8" y1="2" x2="8" y2="6"></line>
                    <line x1="3" y1="10" x2="21" y2="10"></line>
                  </svg>
                  Tarih: {new Date(selectedClass.date_time).toLocaleString("tr-TR")}
                </p>
                <p>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                  </svg>
                  Kalan Kontenjan: {selectedClass.available_spots}
                </p>
                <p>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="1" x2="12" y2="23"></line>
                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                  </svg>
                  {userMembership === 'premium' ? (
                    <>Fiyat: <strong>ÜCRETSİZ</strong></>
                  ) : (
                    <>Fiyat: <strong>₺{calculateUserPrice(selectedClass.base_price, selectedClass.available_spots, selectedClass.capacity, selectedClass.date_time, userMembership).toFixed(2)}</strong></>
                  )}
                </p>
              </div>

              <button className="reservation-button" onClick={handleReservation}>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: "8px" }}>
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                Bu Derse Rezervasyon Yap
              </button>
            </>
          ) : (
            <div className="schedule-selection">
              <div className="selected-class-info">
                <h3>{selectedClass.name}</h3>
                <p>Eğitmen: {selectedClass.instructor_name}</p>
                <p>Tarih: {new Date(selectedClass.date_time).toLocaleString("tr-TR")}</p>
                <p>Kalan Kontenjan: {selectedClass.available_spots}</p>
                <p>Fiyat: ₺{selectedClass.base_price}</p>
              </div>
              
              <div style={{ 
                background: 'linear-gradient(135deg, #f87171 0%, #ef4444 100%)', 
                color: 'white', 
                padding: '1.5rem', 
                borderRadius: '16px', 
                marginTop: '2rem',
                textAlign: 'center',
                boxShadow: '0 10px 30px rgba(239, 68, 68, 0.3)'
              }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '1rem' }}>
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.4rem' }}>Ders Dolu!</h3>
                <p style={{ margin: 0, opacity: 0.9 }}>
                  Bu ders için kontenjan dolmuştur. Lütfen başka bir ders seçin.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}