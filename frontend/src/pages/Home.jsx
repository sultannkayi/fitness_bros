import "./Home.css";
import { Link } from "react-router-dom";

export default function Home() {
  // Sınıflar listesi
  const classes = [
    {
      id: 1,
      name: "Yoga & Esneklik Dersleri",
      description: "Denge, esneklik ve zihinsel netlik kazanmak için rehberli yoga, nefes ve esneme egzersizleriyle antrenmanlarınızı dengeye getirin."
    },
    {
      id: 2,
      name: "Zumba Eğitimi",
      description: "Motivasyon kalabalıkta çoğalır! Zumba, devre antrenmanı, boks ve daha fazlası için enerji dolu grup derslerimize katılın."
    },
    {
      id: 3,
      name: "CrossFit / HIIT Antrenmanları",
      description: "Yüksek yoğunluklu interval antrenmanı ve CrossFit tarzı grup seanslarıyla hızla yağ yakın ve dayanıklılığınızı artırın. Dinamik, tempolu ve eğlenceli."
    }
  ];

  const membershipPlans = [
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

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            İçindeki Gücü <span className="highlight">SERBEST BIRAK</span>
          </h1>
          <p className="hero-subtitle">
            Fitness Bros, bireylere fiziksel sağlık, güç, dayanıklılık, esneklik ve genel fitness'ı 
            geliştirmeyi amaçlayan çeşitli ekipman, dersler ve programlara erişim sağlamak için 
            tasarlanmış bir spor merkezidir.
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
              Fitness BROS'ta, sadece bir spor salonu değiliz—bir topluluğuz. Misyonumuz, 
              ister yeni başlıyor olun ister deneyimli bir sporcu olun, hedeflerinizi aşmanıza 
              yardımcı olmaktır. Ağırlık antrenmanından grup derslerine kadar, uzman eğitmenlerimiz 
              ve son teknoloji ekipmanlarımız limitlerini zorlamanız için burada.
            </p>
            
            <div className="features">
              <div className="feature-item">
                <span className="feature-icon">💪</span>
                <div>
                  <h3 className="feature-number">01.</h3>
                  <h4 className="feature-title">24/7 ERİŞİM</h4>
                  <p className="feature-text">
                    Hayat meşgul — spor salonunuz programınıza uymalı, tam tersi değil. 
                    İster sabahın erken saatlerinde ister gece kuşu olun, salonumuz 7/24 açık, 
                    böylece size en uygun zamanda çalışabilirsiniz.
                  </p>
                </div>
              </div>

              <div className="feature-item">
                <span className="feature-icon">🎓</span>
                <div>
                  <h3 className="feature-number">02.</h3>
                  <h4 className="feature-title">SERTİFİKALI EĞİTMENLER</h4>
                  <p className="feature-text">
                    Sertifikalı, deneyimli eğitmen ekibimiz tam potansiyelinizi ortaya çıkarmanıza 
                    yardımcı olmak için burada. Yeni başlayanlardan sporculara kadar, güvenli, 
                    etkili ve motive edici kişiselleştirilmiş koçluk sağlıyoruz.
                  </p>
                </div>
              </div>

              <div className="feature-item">
                <span className="feature-icon">🛡️</span>
                <div>
                  <h3 className="feature-number">03.</h3>
                  <h4 className="feature-title">TEMİZ & GÜVENLİ ORTAM</h4>
                  <p className="feature-text">
                    En yüksek temizlik ve güvenlik standartlarını koruyoruz. Tesisimiz günlük 
                    olarak dezenfekte edilir ve ekipmanlarımız düzenli olarak kontrol edilip 
                    bakımı yapılır — böylece endişesizce sağlığınıza odaklanabilirsiniz.
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
              <Link to="/profile">
                  <button className="plan-cta">HEMEN BAŞLA</button>
              </Link>
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
              <h4 className="footer-title orange">İletişim</h4>
              <ul>
                <li>📍 Sarıçam, Adana</li>
                <li>📞 Bizi Arayın: +90 919 245 07 890</li>
                <li>✉️ E-posta: info@fitnessbros.com</li>
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
