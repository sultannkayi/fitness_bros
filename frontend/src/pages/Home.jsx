import "./Home.css";
import { Link } from "react-router-dom";

export default function Home() {
  // Test için kasıtlı syntax hatası - pipeline test
  const testVariable = undefinedFunction();
  
  // Sınıflar listesi
  const classes = [
    {
      id: 1,
      name: "Yoga & Esneklik Dersleri",
      description: "Balance your strength training with guided yoga, breathing, and stretching exercises that improve flexibility, posture, and mental clarity.Balance your strength training with guided yoga, breathing, and stretching exercises that improve flexibility, posture, and mental clarity."
    },
    {
      id: 2,
      name: "Zumba Eğitimi",
      description: "Motivation multiplies in a crowd! Join our energy-packed group classes for Zumba, circuit training, boxing, and more.Motivation multiplies in a crowd! Join our energy-packed group classes for Zumba, circuit training, boxing, and more."
    },
    {
      id: 3,
      name: "CrossFit / HIIT Antrenmanları",
      description: "Burn fat fast and increase stamina with high-intensity interval training and CrossFit-style group sessions. Dynamic, fast-paced, and fun.Burn fat fast and increase stamina with high-intensity interval training and CrossFit-style group sessions. Dynamic, fast-paced, and fun."
    }
  ];

  const membershipPlans = [
    {
      name: "BAŞLANGIÇ PAKETİ",
      price: "999",
      features: [
        "Spor salonuna sınırsız erişim",
        "Haftada 5 ders hakkı"
      ]
    },
    {
      name: "PREMIUM PAKET",
      price: "1499",
      features: [
        "Spor salonuna sınırsız erişim",
        "Haftada 5 ders hakkı",
        "1 Yıllık Üyelik Avantajı"
      ]
    },
    {
      name: "ULTIMATE PAKET",
      price: "1999",
      features: [
        "Spor salonuna sınırsız erişim",
        "Haftada 5 ders hakkı",
        "1 Yıllık Üyelik Avantajı",
        "ÜCRETSİZ içecek paketi",
        "2 Ücretsiz kişisel antrenman"
      ]
    }
  ];

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            İçindeki Gücü <span className="highlight">SERBEST BIRAK</span>
          </h1>
          <p className="hero-subtitle">
            A ironfit fitness center is a facility designed to provide individuals with access to
            various equipment, classes, and programs aimed at improving physical health,
            strength, endurance, flexibility, and overall fitness.
          </p>
          <Link to="/reservations">
            <button className="cta-button">HEMEN KATIL</button>
          </Link>
        </div>
      </section>

      {/* Classes Section */}
      <section id="classes-section" className="classes-section">
        <h2 className="section-title">
          SINIFLARIMIZ
        </h2>
        
        <div className="classes-grid">
          {classes.map((fitnessClass, index) => (
            <div key={fitnessClass.id} className="class-card">
              <div className="class-image-container">
                <div className="class-image-placeholder">
                  {/* Placeholder for class image */}
                  <span className="class-number">{index + 1}</span>
                </div>
              </div>
              <div className="class-info">
                <h3 className="class-name">
                  <span className="bullet">•</span> {fitnessClass.name}
                </h3>
                <p className="class-description">{fitnessClass.description}</p>
                <Link to="/reservations">
                  <button className="class-cta">HEMEN KATIL</button>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* About Section */}
      <section id="about-section" className="about-section">
        <div className="about-content">
          <div className="about-text">
            <h2 className="about-title">
              <span className="brand">Fitness BROS</span>'la ilgili
            </h2>
            <p className="about-description">
              At Fitness BROS, we're not just a gym—we're a community. Our mission is to
              help you crush your goals, whether you're just starting out or a seasoned
              athlete. From weight training to group classes, our expert trainers and state-
              of-the-art equipment are here to push your limits.
            </p>
            
            <div className="features">
              <div className="feature-item">
                <span className="feature-icon">💪</span>
                <div>
                  <h3 className="feature-number">01.</h3>
                  <h4 className="feature-title">24/7 ERİŞİM</h4>
                  <p className="feature-text">
                    Life is busy — your gym should fit your schedule, not the other way around.
                    Whether you're an early bird or a night owl, our Fitness is open 24/7, so you
                    can work out when it works best for you.
                  </p>
                </div>
              </div>

              <div className="feature-item">
                <span className="feature-icon">🎓</span>
                <div>
                  <h3 className="feature-number">02.</h3>
                  <h4 className="feature-title">SERTİFİKALI EĞİTMENLER</h4>
                  <p className="feature-text">
                    Our team of certified, experienced trainers is here to help you unlock your full
                    potential. From beginners to athletes, we provide personalized coaching that's
                    safe, effective, and motivating.
                  </p>
                </div>
              </div>

              <div className="feature-item">
                <span className="feature-icon">🛡️</span>
                <div>
                  <h3 className="feature-number">03.</h3>
                  <h4 className="feature-title">TEMİZ & GÜVENLİ ORTAM</h4>
                  <p className="feature-text">
                    We maintain the highest standards of cleanliness and safety. Our facility is
                    sanitized daily, and our equipment is regularly inspected and maintained — so
                    you can focus on your health, worry-free.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="about-image">
            <div className="about-image-content">
              <h2 className="about-image-title">
                Real<br />
                <span className="orange">PEOPLE,</span><br />
                Real<br />
                <span className="orange">RESULTS</span>
              </h2>
              <p className="about-image-subtitle">
                <span className="orange">FITNESS</span> FITNESS
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Membership Plans Section */}
      <section className="membership-section">
        <h2 className="section-title membership-title">
          Esnek <span className="orange">ÜYELİK</span> Planları
        </h2>
        
        <div className="plans-grid">
          {membershipPlans.map((plan, index) => (
            <div key={index} className={`plan-card ${index === 1 ? 'featured' : ''}`}>
              <h3 className="plan-name">{plan.name}</h3>
              <div className="plan-price">
                <span className="price">{plan.price}</span>
                <span className="period">₺ / aylık</span>
              </div>
              <ul className="plan-features">
                {plan.features.map((feature, fIndex) => (
                  <li key={fIndex}>
                    <span className="check">✓</span> {feature}
                  </li>
                ))}
              </ul>
              <button className="plan-cta">HEMEN BAŞLA</button>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer id="contact-section" className="footer">
        <div className="footer-content">
          <div className="footer-brand">
            <h2 className="footer-logo">
              Fitness <span className="orange">BROS</span>
            </h2>
          </div>
          
          <div className="footer-links">
            <div className="footer-column">
              <h4 className="footer-title orange">Hızlı Bağlantılar</h4>
              <ul>
                <li>Sınıflarımız</li>
                <li>Bize Ulaşın</li>
                <li>Programlarımız</li>
              </ul>
            </div>
            
            <div className="footer-column">
              <h4 className="footer-title orange">Get In Touch</h4>
              <ul>
                <li>📍 Sarıçam, Adana</li>
                <li>📞 Call Us: +91 919 245 07 890</li>
                <li>✉️ Email Us: info@fitnessbros.com</li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>© 2025 Fitness Bros. Tüm hakları saklıdır.</p>
        </div>
      </footer>
    </div>
  );
}
