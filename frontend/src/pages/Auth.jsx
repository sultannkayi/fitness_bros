import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Auth.css";

export default function Auth() {
  const navigate = useNavigate();
  const [isSignUp, setIsSignUp] = useState(false); // false = Sign In ilk gelir
  
  const [signInData, setSignInData] = useState({
    email: "",
    password: ""
  });

  const [signUpData, setSignUpData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    gender: "",
    dateOfBirth: "",
    height: "",
    weight: ""
  });

  const handleSignInSubmit = (e) => {
    e.preventDefault();
    // Backend'e sign in isteği
    console.log("Sign In:", signInData);
    // Başarılı girişten sonra profile'a yönlendir
    navigate('/profile');
  };

  const handleSignUpSubmit = (e) => {
    e.preventDefault();
    // Backend'e sign up isteği
    console.log("Sign Up:", signUpData);
    // Başarılı kayıttan sonra profile'a yönlendir
    navigate('/profile');
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1 className="auth-brand">
            Fitness <span className="brand-highlight">BROS</span>
          </h1>
          <p className="auth-subtitle">İçindeki Gücü Serbest Bırak</p>
        </div>

        <div className="auth-toggle">
          <button 
            className={`toggle-btn ${!isSignUp ? 'active' : ''}`}
            onClick={() => setIsSignUp(false)}
          >
            Giriş Yap
          </button>
          <button 
            className={`toggle-btn ${isSignUp ? 'active' : ''}`}
            onClick={() => setIsSignUp(true)}
          >
            Kayıt Ol
          </button>
        </div>

        {!isSignUp ? (
          // Sign In Form
          <form className="auth-form" onSubmit={handleSignInSubmit}>
            <h2 className="form-title">Giriş Yap</h2>
            
            <div className="form-group">
              <label htmlFor="signin-email">E-posta / Kullanıcı Adı</label>
              <input
                type="text"
                id="signin-email"
                value={signInData.email}
                onChange={(e) => setSignInData({...signInData, email: e.target.value})}
                placeholder="ornek@email.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="signin-password">Şifre</label>
              <input
                type="password"
                id="signin-password"
                value={signInData.password}
                onChange={(e) => setSignInData({...signInData, password: e.target.value})}
                placeholder="••••••••"
                required
              />
            </div>

            <button type="submit" className="submit-btn">
              Giriş Yap
            </button>

            <p className="form-footer">
              Hesabınız yok mu? 
              <span className="link" onClick={() => setIsSignUp(true)}> Kayıt Ol</span>
            </p>
          </form>
        ) : (
          // Sign Up Form
          <form className="auth-form" onSubmit={handleSignUpSubmit}>
            <h2 className="form-title">Kayıt Ol</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="signup-firstname">İsim *</label>
                <input
                  type="text"
                  id="signup-firstname"
                  value={signUpData.firstName}
                  onChange={(e) => setSignUpData({...signUpData, firstName: e.target.value})}
                  placeholder="İsim"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="signup-lastname">Soyisim *</label>
                <input
                  type="text"
                  id="signup-lastname"
                  value={signUpData.lastName}
                  onChange={(e) => setSignUpData({...signUpData, lastName: e.target.value})}
                  placeholder="Soyisim"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="signup-email">E-posta *</label>
              <input
                type="email"
                id="signup-email"
                value={signUpData.email}
                onChange={(e) => setSignUpData({...signUpData, email: e.target.value})}
                placeholder="ornek@email.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="signup-password">Şifre *</label>
              <input
                type="password"
                id="signup-password"
                value={signUpData.password}
                onChange={(e) => setSignUpData({...signUpData, password: e.target.value})}
                placeholder="••••••••"
                required
                minLength="6"
              />
            </div>

            <div className="form-group">
              <label htmlFor="signup-gender">Cinsiyet *</label>
              <select
                id="signup-gender"
                value={signUpData.gender}
                onChange={(e) => setSignUpData({...signUpData, gender: e.target.value})}
                required
              >
                <option value="">Seçiniz</option>
                <option value="male">Erkek</option>
                <option value="female">Kadın</option>
                <option value="other">Diğer</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="signup-dob">Doğum Tarihi *</label>
              <input
                type="date"
                id="signup-dob"
                value={signUpData.dateOfBirth}
                onChange={(e) => setSignUpData({...signUpData, dateOfBirth: e.target.value})}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="signup-height">Boy (cm) *</label>
                <input
                  type="number"
                  id="signup-height"
                  value={signUpData.height}
                  onChange={(e) => setSignUpData({...signUpData, height: e.target.value})}
                  placeholder="175"
                  required
                  min="100"
                  max="250"
                />
              </div>

              <div className="form-group">
                <label htmlFor="signup-weight">Kilo (kg) *</label>
                <input
                  type="number"
                  id="signup-weight"
                  value={signUpData.weight}
                  onChange={(e) => setSignUpData({...signUpData, weight: e.target.value})}
                  placeholder="70"
                  required
                  min="30"
                  max="300"
                />
              </div>
            </div>

            <button type="submit" className="submit-btn">
              Kayıt Ol
            </button>

            <p className="form-footer">
              Zaten hesabınız var mı? 
              <span className="link" onClick={() => setIsSignUp(false)}> Giriş Yap</span>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
