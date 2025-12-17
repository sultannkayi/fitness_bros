import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Reservations.css";

export default function Reservations() {
  const navigate = useNavigate();
  const [selectedClass, setSelectedClass] = useState(null);
  const [selectedSchedule, setSelectedSchedule] = useState(null);

  // Sınıf verileri - Backend'den gelecek
  const fitnessClasses = [
    {
      id: 1,
      name: "Yoga & Esneklik Dersleri",
      instructor: "Ayşe Demir",
      capacity: 15,
      description: "Vücut esnekliğinizi artırın, zihninizi dinlendirin ve iç dengenizi bulun.",
      schedule: [
        { day: "Pazartesi", time: "09:00", available: 12 },
        { day: "Çarşamba", time: "18:00", available: 8 }
      ]
    },
    {
      id: 2,
      name: "Zumba Eğitimi",
      instructor: "Mert Yılmaz",
      capacity: 20,
      description: "Enerjik müzik eşliğinde dans ederek kalori yakın ve eğlenin.",
      schedule: [
        { day: "Salı", time: "19:00", available: 15 },
        { day: "Perşembe", time: "20:00", available: 5 }
      ]
    },
    {
      id: 3,
      name: "CrossFit / HIIT Antrenmanları",
      instructor: "Can Öztürk",
      capacity: 12,
      description: "Yüksek yoğunluklu interval antrenmanlarıyla gücünüzü ve dayanıklılığınızı artırın.",
      schedule: [
        { day: "Çarşamba", time: "07:00", available: 10 },
        { day: "Cuma", time: "18:30", available: 3 }
      ]
    }
  ];

  const handleClassSelect = (classData) => {
    setSelectedClass(classData);
    setSelectedSchedule(null);
  };

  const handleScheduleSelect = (schedule) => {
    setSelectedSchedule(schedule);
  };

  const handleReservation = () => {
    if (!selectedClass || !selectedSchedule) {
      alert("Lütfen bir sınıf ve saat seçin!");
      return;
    }

    // Rezervasyon bilgisini oluştur
    const reservation = {
      id: Date.now(),
      className: selectedClass.name,
      instructor: selectedClass.instructor,
      day: selectedSchedule.day,
      time: selectedSchedule.time,
      date: new Date().toLocaleDateString('tr-TR'),
      status: 'Onaylandı'
    };

    // Mevcut rezervasyonları al
    const existingReservations = JSON.parse(localStorage.getItem('reservations') || '[]');
    
    // Yeni rezervasyonu ekle
    existingReservations.push(reservation);
    
    // localStorage'a kaydet
    localStorage.setItem('reservations', JSON.stringify(existingReservations));

    // Backend'e rezervasyon isteği gönderilecek
    console.log("Rezervasyon:", {
      classId: selectedClass.id,
      day: selectedSchedule.day,
      time: selectedSchedule.time
    });

    alert(`${selectedClass.name} - ${selectedSchedule.day} ${selectedSchedule.time} için rezervasyonunuz alındı!`);
    
    // Başarılı rezervasyon sonrası profile'a yönlendir
    navigate('/profile');
  };

  return (
    <div className="reservations-page">
      <div className="reservations-container">
        <div className="reservations-header">
          <h1 className="reservations-title">
            Sınıf <span className="highlight">REZERVASYONU</span>
          </h1>
          <p className="reservations-subtitle">
            Size uygun sınıfı ve zamanı seçin, hemen rezervasyon yapın!
          </p>
        </div>

        <div className="reservations-content">
          {/* Sol Taraf - Sınıf Listesi */}
          <div className="classes-list">
            <h2 className="list-title">Sınıflarımız</h2>
            {fitnessClasses.map((classData) => (
              <div
                key={classData.id}
                className={`class-item ${selectedClass?.id === classData.id ? 'selected' : ''}`}
                onClick={() => handleClassSelect(classData)}
              >
                <div className="class-item-header">
                  <h3 className="class-item-name">{classData.name}</h3>
                  <span className="class-capacity">
                    Kapasite: {classData.capacity} kişi
                  </span>
                </div>
                <p className="class-instructor">
                  👤 Eğitmen: <strong>{classData.instructor}</strong>
                </p>
                <p className="class-description">{classData.description}</p>
              </div>
            ))}
          </div>

          {/* Sağ Taraf - Saat Seçimi */}
          <div className="schedule-selection">
            {selectedClass ? (
              <>
                <h2 className="list-title">Gün & Saat Seçin</h2>
                <div className="selected-class-info">
                  <h3>{selectedClass.name}</h3>
                  <p>Eğitmen: {selectedClass.instructor}</p>
                </div>

                <div className="schedule-grid">
                  {selectedClass.schedule.map((schedule, index) => (
                    <div
                      key={index}
                      className={`schedule-card ${selectedSchedule === schedule ? 'selected' : ''} ${schedule.available === 0 ? 'full' : ''}`}
                      onClick={() => schedule.available > 0 && handleScheduleSelect(schedule)}
                    >
                      <div className="schedule-day">{schedule.day}</div>
                      <div className="schedule-time">{schedule.time}</div>
                      <div className="schedule-availability">
                        {schedule.available > 0 ? (
                          <span className="available">
                            ✓ {schedule.available}/{selectedClass.capacity} Boş
                          </span>
                        ) : (
                          <span className="unavailable">✗ Dolu</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {selectedSchedule && (
                  <button className="reservation-button" onClick={handleReservation}>
                    Rezervasyon Yap
                  </button>
                )}
              </>
            ) : (
              <div className="no-selection">
                <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M8 2v4M16 2v4M3.5 9.09h17M21 8.5V17c0 3-1.5 5-5 5H8c-3.5 0-5-2-5-5V8.5c0-3 1.5-5 5-5h8c3.5 0 5 2 5 5Z"/>
                  <path d="M11.995 13.7h.009M8.295 13.7h.009M8.295 16.7h.01"/>
                </svg>
                <h3>Sınıf Seçin</h3>
                <p>Soldaki listeden rezervasyon yapmak istediğiniz sınıfı seçin</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
