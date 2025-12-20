import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Reservations.css";

export default function Reservations() {
  const navigate = useNavigate();
  const location = useLocation();
  const [fitnessClasses, setFitnessClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState(null);
  const [selectedSchedule, setSelectedSchedule] = useState(null);

  const loadClassesFromStorage = () => {
    const stored = JSON.parse(localStorage.getItem("fitnessClasses"));
    if (stored && Array.isArray(stored) && stored.length > 0) {
      setFitnessClasses(stored);
    } else {
      const defaultClasses = [
        {
          id: 1,
          name: "Yoga",
          instructor: "Ayşe Demir",
          capacity: 15,
          schedule: [
            { day: "Pazartesi", time: "09:00", available: 12 },
            { day: "Çarşamba", time: "18:00", available: 8 },
          ],
        },
        {
          id: 2,
          name: "Zumba",
          instructor: "Mert Yılmaz",
          capacity: 20,
          schedule: [
            { day: "Salı", time: "19:00", available: 15 },
            { day: "Perşembe", time: "20:00", available: 5 },
          ],
        },
        {
          id: 3,
          name: "CrossFit",
          instructor: "Can Öztürk",
          capacity: 12,
          schedule: [
            { day: "Çarşamba", time: "07:00", available: 10 },
            { day: "Cuma", time: "18:30", available: 3 },
          ],
        },
      ];
      localStorage.setItem("fitnessClasses", JSON.stringify(defaultClasses));
      setFitnessClasses(defaultClasses);
    }
  };

  // Load classes on mount and when location changes
  useEffect(() => {
    loadClassesFromStorage();
    setSelectedClass(null);
    setSelectedSchedule(null);
  }, [location]);

  // Reload when window gains focus
  useEffect(() => {
    const handleFocus = () => {
      loadClassesFromStorage();
      setSelectedClass(null);
      setSelectedSchedule(null);
    };

    const handleStorageChange = (e) => {
      if (e.key === "fitnessClasses") {
        loadClassesFromStorage();
      }
    };

    window.addEventListener("focus", handleFocus);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("focus", handleFocus);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  const handleClassSelect = (cls) => {
    setSelectedClass(cls);
    setSelectedSchedule(null);
  };

  const handleScheduleSelect = (sch) => {
    if (sch.available === 0) return;
    setSelectedSchedule(sch);
  };

  const handleReservation = () => {
    const userData = JSON.parse(localStorage.getItem("userData"));
    if (!userData) {
      navigate("/auth");
      return;
    }

    const reservations = JSON.parse(localStorage.getItem("reservations")) || [];
    const alreadyBooked = reservations.some(
      (r) =>
        r.user === userData.name &&
        r.className === selectedClass.name &&
        r.day === selectedSchedule.day &&
        r.time === selectedSchedule.time
    );

    if (alreadyBooked) {
      alert("Bu derse aynı saat için zaten rezervasyonunuz var.");
      return;
    }

    if (selectedSchedule.available <= 0) return;

    const reservation = {
      id: Date.now(),
      user: userData.name,
      className: selectedClass.name,
      instructor: selectedClass.instructor,
      day: selectedSchedule.day,
      time: selectedSchedule.time,
      date: new Date().toLocaleDateString("tr-TR"),
      status: "Onaylandı",
    };

    const updatedClasses = fitnessClasses.map((cls) => {
      if (cls.id !== selectedClass.id) return cls;
      return {
        ...cls,
        schedule: cls.schedule.map((sch) =>
          sch.day === selectedSchedule.day && sch.time === selectedSchedule.time
            ? { ...sch, available: sch.available - 1 }
            : sch
        ),
      };
    });

    localStorage.setItem(
      "reservations",
      JSON.stringify([...reservations, reservation])
    );
    localStorage.setItem("fitnessClasses", JSON.stringify(updatedClasses));
    setFitnessClasses(updatedClasses);
    navigate("/profile");
  };

  return (
    <div className="reservations-page">
      <div className="classes-list">
        {fitnessClasses.map((cls) => (
          <div
            key={cls.id}
            className={`class-item ${
              selectedClass?.id === cls.id ? "selected" : ""
            }`}
            onClick={() => handleClassSelect(cls)}
          >
            <h3>{cls.name}</h3>
            <p>{cls.instructor}</p>
          </div>
        ))}
      </div>
      <div className="schedule-selection">
        {selectedClass &&
          selectedClass.schedule.map((sch, i) => (
            <div
              key={i}
              className={`schedule-card ${
                sch.available === 0 ? "full" : ""
              } ${selectedSchedule === sch ? "selected" : ""}`}
              onClick={() => handleScheduleSelect(sch)}
            >
              <span>{sch.day}</span>
              <span>{sch.time}</span>
              <span>{sch.available} boş</span>
            </div>
          ))}
        {selectedSchedule && (
          <button className="reservation-button" onClick={handleReservation}>
            Rezervasyon Yap
          </button>
        )}
      </div>
    </div>
  );
}