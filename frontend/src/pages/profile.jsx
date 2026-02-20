import { useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import api from "../api";
import "./Profile.css";
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';
import { useSearchParams } from "react-router-dom";

const MySwal = withReactContent(Swal);


const PLAN_TYPES = [
  {
    id: 'student',
    name: 'Öğrenci Paketi',
    price: '₺500/ay',
    features: [
      '%20 Ders İndirimi',
      'İptalde %50 İade (24 saat önceden)',
      'Maksimum 3 Gelecek Tarihli Rezervasyon',
      'Öğrenci Kimliği ile Uygun Fiyat'
    ]
  },
  {
    id: 'standard',
    name: 'Standart Paket',
    price: '₺1000/ay',
    features: [
      'Tam Fiyat Erişimi',
      'İptal İadesi Yok',
      'Maksimum 5 Gelecek Tarihli Rezervasyon',
      'Tüm Derslere Standart Erişim'
    ]
  },
  {
    id: 'premium',
    name: 'Premium Paket',
    price: '₺2500/ay',
    features: [
      'Dersler TAMAMEN ÜCRETSİZ',
      '%100 İptal İadesi',
      'Dinamik Fiyatlandırma Etkisi Yok',
      'Maksimum 10 Gelecek Tarihli Rezervasyon',
      'Öncelikli Kayıt ve Sınırsız Erişim'
    ]
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
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/auth", { replace: true });
      return;
    }
    loadData();
  }, [navigate]);

  const loadData = useCallback(async () => {
    try {
      const currentToken = localStorage.getItem("access_token");
      if (!currentToken) {
        navigate("/auth");
        return;
      }

      const userResponse = await api.get("/memberships/me/");
      setUserData(userResponse.data);

      const resResponse = await api.get("/reservations/");
      setReservations(resResponse.data);

      const classesResponse = await api.get("/classes/");
      setFitnessClasses(classesResponse.data);
    } catch (err) {
      console.error("Veri yükleme hatası:", err);
      if (err.response?.status === 401 || err.response?.status === 403) {
        localStorage.removeItem("access_token");
        navigate("/auth");
      }
    }
  }, [navigate]);

  useEffect(() => {
    loadData();
  }, [location, loadData]);

  useEffect(() => {
    const handleFocus = () => loadData();
    window.addEventListener("focus", handleFocus);
    return () => window.removeEventListener("focus", handleFocus);
  }, [loadData]);

  // Callback sonrası URL'deki payment parametresine göre bilgilendirme
  useEffect(() => {
    const paymentStatus = searchParams.get('payment');
    if (paymentStatus === 'success') {
      MySwal.fire({
        icon: 'success',
        title: 'Başarılı!',
        text: 'Üyeliğiniz güncellendi. Teşekkürler!',
        timer: 4000,
        timerProgressBar: true,
      });
      navigate('/profile', { replace: true });
    } else if (paymentStatus === 'failed') {
      MySwal.fire({
        icon: 'error',
        title: 'Ödeme Başarısız',
        text: 'Ödeme işlemi tamamlanamadı. Lütfen tekrar deneyin.',
      });
      navigate('/profile', { replace: true });
    }
  }, [searchParams, navigate]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/auth", { replace: true });
  };

  // PAKET GÜNCELLEME
  const handlePlanUpdate = async () => {
    if (!selectedPlan) return;

    // Mevcut rezervasyon kontrolü
    const now = new Date();
    const activeReservations = reservations.filter(r => {
      const dateString = r.fitness_class?.date_time || r.day;
      if (!dateString) return false;
      const classDate = new Date(dateString);
      return classDate > now;
    });

    if (activeReservations.length > 0) {
      const result = await MySwal.fire({
        icon: 'warning',
        title: 'Dikkat!',
        text: 'Gelecek tarihli aktif rezervasyonlarınız bulunmaktadır. Paket değişikliği bu rezervasyonları etkileyebilir.',
        showCancelButton: true,
        confirmButtonText: 'Yine de Devam Et',
        cancelButtonText: 'Vazgeç',
      });
      if (!result.isConfirmed) return;
    }

    const confirmResult = await MySwal.fire({
      icon: 'question',
      title: 'Onaylıyor musunuz?',
      text: `${selectedPlan.name} (${selectedPlan.price}) paketine geçmek istediğinize emin misiniz?`,
      showCancelButton: true,
      confirmButtonText: 'Evet, Geç',
      cancelButtonText: 'İptal',
    });

    if (!confirmResult.isConfirmed) return;

    try {
      // Ödeme başlatma
      const response = await api.post('/payment/initiate-membership/', {
        membership_type: selectedPlan.id,
      });

      if (response.data.status === 'success' && response.data.payment_page_url) {
        window.location.href = response.data.payment_page_url;
      } else {
        throw new Error(response.data.message || 'Ödeme başlatılamadı');
      }
    } catch (err) {
      console.error('Ödeme başlatma hatası:', err);
      let errorMessage = 'Ödeme işlemi başlatılamadı.';
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      }

      MySwal.fire({
        icon: 'error',
        title: 'Hata!',
        text: errorMessage,
      });
    }
  };

  // REZERVASYON İPTAL
  const handleCancelReservation = async (id) => {
    const reservation = reservations.find(r => r.id === id);
    if (!reservation) return;

    const pricePaid = parseFloat(reservation.price_paid || 0);
    const dateString = reservation.fitness_class?.date_time || reservation.day;
    const classDate = new Date(dateString);
    const now = new Date();
    const hoursRemaining = (classDate - now) / (1000 * 60 * 60);

    const membershipType = userData?.membership_type || 'standard';

    let refundAmount = 0;
    if (membershipType === 'premium' && hoursRemaining >= 2) refundAmount = pricePaid;
    else if (membershipType === 'student' && hoursRemaining >= 24) refundAmount = pricePaid * 0.5;

    const message = `
REZERVASYON İPTAL DETAYLARI
--------------------------------
Ders: ${reservation.fitness_class?.name || 'Fitness Dersi'}
Ödenen Tutar: ${pricePaid.toFixed(2)}₺
Kalan Süre: ${hoursRemaining > 0 ? hoursRemaining.toFixed(1) + ' saat' : 'Süre doldu'}

İADE DURUMU:
--------------------------------
Paketiniz: ${PLAN_TYPES.find(p => p.id === membershipType)?.name || membershipType}
Tahmini İade: ${refundAmount.toFixed(2)}₺

İptal işlemini onaylıyor musunuz?`;

    const confirmResult = await MySwal.fire({
      icon: 'warning',
      title: 'İptal Onayı',
      html: message.replace(/\n/g, '<br>'),
      showCancelButton: true,
      confirmButtonText: 'Evet, İptal Et',
      cancelButtonText: 'Vazgeç',
    });

    if (!confirmResult.isConfirmed) return;

    try {
      await api.delete(`/reservations/${id}/`);
      await loadData();
      MySwal.fire({
        icon: 'success',
        title: 'İptal Edildi',
        text: `Rezervasyon iptal edildi.${refundAmount > 0 ? ` ${refundAmount.toFixed(2)}₺ iade edilecektir.` : ''}`,
        timer: 3000,
        timerProgressBar: true,
      });
    } catch (err) {
      console.error("İptal hatası:", err);
      MySwal.fire({
        icon: 'error',
        title: 'Hata',
        text: 'İptal sırasında bir sorun oluştu.',
      });
    }
  };

  const getCurrentPlanInfo = () => {
    if (!userData?.membership_type) return "Plan Seçilmedi";
    const plan = PLAN_TYPES.find(p => p.id === userData.membership_type);
    return plan ? `${plan.name}` : "Plan Seçilmedi";
  };

  if (!userData) {
    return (
      <div className="profile-page">
        <p>Yükleniyor...</p>
      </div>
    );
  }

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
              <h2 className="profile-name">{userData.name || userData.username}</h2>
              <button className="profile-plan-button" onClick={() => setShowPlanModal(true)}>
                {getCurrentPlanInfo()} <span style={{marginLeft: '5px', fontSize: '0.8em'}}>✎</span>
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
            </div>
            <div className="profile-details">
              <div className="detail-row">
                <span className="detail-label">Name</span>
                <span className="detail-value">{userData.name || userData.username}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Gender</span>
                <span className="detail-value">{userData.gender}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Date of birth</span>
                <span className="detail-value">{userData.dateOfBirth || userData.birth_date}</span>
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
                + Yeni Rezervasyon
              </button>
              {reservations.length > 0 ? (
                <div className="reservations-list">
                  {reservations.map((r) => (
                    <div key={r.id} className="reservation-item">
                      <div className="reservation-header">
                        <h4 className="reservation-class-name">
                            {r.fitness_class?.name || r.className || 'Ders'}
                        </h4>
                        <span className="reservation-status confirmed">
                          Onaylı
                        </span>
                      </div>
                      <p className="reservation-instructor">
                        👤 Eğitmen: {r.fitness_class?.instructor || r.instructor || '-'}
                      </p>
                      <div className="reservation-details">
                        {/* Tarih formatı backend'den gelene göre ayarlanabilir */}
                        <span>📅 {new Date(r.fitness_class?.date_time || r.day || Date.now()).toLocaleDateString('tr-TR')}</span>
                        <span>🕐 {new Date(r.fitness_class?.date_time || r.time || Date.now()).toLocaleTimeString('tr-TR', {hour: '2-digit', minute:'2-digit'})}</span>
                      </div>
                      
                      <div style={{fontSize: '0.9em', color: '#666', marginBottom: '10px'}}>
                         Ödenen: <strong>{r.price_paid}₺</strong>
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
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
            maxHeight: '90vh',
            overflowY: 'auto'
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