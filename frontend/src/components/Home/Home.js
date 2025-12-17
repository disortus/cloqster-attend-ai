import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home-page">

      {/* Hero секция */}
      <section className="hero">
        <div className="hero-content">
          <p className="hero-badge">Кешікпеу → Оңай</p>
          <h1 className="hero-title">CloqsterAI</h1>
          <h2 className="hero-subtitle">Оқу жетістігін қадағалау веб-сайты</h2>
          <p className="hero-desc">
            Біздің веб-сайтымыз барлық кәсіпорындар, оқу орындары және жалпы барлығы үшін өмірді жеңілдетеді, кәсіпорындағы үлгерім мен келу/кету уақытын оңай бақылауға мүмкіндік береді.
          </p>
          <div className="hero-buttons">
            <Link to="/mark" className="btn-primary">Қазір Белгі Қою</Link>
            <Link to="/how-it-works" className="btn-secondary">Қалай жұмыс істейді?</Link>
          </div>
        </div>
      </section>

      {/* Преимущества — 6 карточек */}
      <section className="features-section">
        <h2 className="section-title">Here CloqsterAI?</h2>
        <p className="section-subtitle">
          Әр-түрлі компаниялар мен оқу орындардың қатысуды қадағалау үшін қажетті барлық құралдар
        </p>

        <div className="cards-grid">
          <div className="feature-card">
            <div className="card-icon">📷</div>
            <h3>Камера арқылы Белгі Қою</h3>
            <p>Белгі қоюды тексергіңіз келе ме? селфи жасап көріңіз!</p>
          </div>
          <div className="feature-card">
            <div className="card-icon">⏱</div>
            <h3>Нақты уақыт көрсету</h3>
            <p>Бүкіл минутына дейін санап береді!</p>
          </div>
          <div className="feature-card">
            <div className="card-icon">📊</div>
            <h3>Есеп және Аналитика</h3>
            <p>Басқарушылар үшін толық аналитика, есептер және фильтрлер ұсынысы.</p>
          </div>
          <div className="feature-card">
            <div className="card-icon">🔒</div>
            <h3>Құпиялылық және Қауіпсіздік</h3>
            <p>Құпиялық саясат расталған және барлық заңдық актілерді сақтайды.</p>
          </div>
          <div className="feature-card">
            <div className="card-icon">👥</div>
            <h3>TeamView</h3>
            <p>Студент және мұғалім өзара әрекеттеседі</p>
          </div>
          <div className="feature-card">
            <div className="card-icon">📱</div>
            <h3>Мобильді Жүйе</h3>
            <p>Барлық нәрсе кез келген браузерде оңай қолжетімді және жылдам жұмыс істейді</p>
          </div>
        </div>
      </section>

      {/* Как работает — 3 шага */}
      <section className="how-section">
        <h2 className="section-title">Қалай жұмыс істейді?</h2>
        <p className="section-subtitle">Үш қадам.</p>

        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3>Камераны іске қосу</h3>
            <p>Сіздің құрылғыңыздың камерасына рұқсат беріңіз.</p>
          </div>
          <div className="step-card">
            <div className="step-number">2</div>
            <h3>Сканерлеу</h3>
            <p>"Белгі қою" басыңыз — FACEID сканерлейді.</p>
          </div>
          <div className="step-card">
            <div className="step-number">3</div>
            <h3>Аяқтау және Аналитика</h3>
            <p>Статус, уақыт белгісі және басқа деректер.</p>
          </div>
        </div>
      </section>

      {/* Для кого — две карточки */}
      <section className="for-who-section">
        <h2 className="section-title">Панельдер</h2>
        <p className="section-subtitle">Пайдаланушылар және басқарушылар үшін орындалған</p>

        <div className="for-who-grid">
          <div className="user-card">
            <div className="card-icon">👤</div>
            <h3>Пайдаланушылар үшін</h3>
            <ul>
              <li>Оңай белгі қою</li>
              <li>Тарих</li>
              <li>Уақыт статусын тез білу</li>
            </ul>
            <Link to="/mark" className="btn-small blue">Белгі қою</Link>
          </div>

          <div className="admin-card">
            <div className="card-icon">📊</div>
            <h3>Басқарушылар үшін</h3>
            <ul>
              <li>Оқу процесін толық бақылау</li>
              <li>Есептер және аналитиканы көру</li>
            </ul>
            <Link to="/admin" className="btn-small purple">Басқарушы Панелі</Link>
          </div>
        </div>
      </section>

      {/* Нижний CTA */}
      <section className="cta-section">
        <h2 className="cta-title">Байланысу.</h2>
        <div className="cta-buttons">
          <Link to="/register" className="btn-light">Акысыз Тіркелу</Link>
          <a href="mailto:support@cloqster.ai" className="btn-blue">Бізге Хабарласыңыз</a>
        </div>
      </section>
    </div>
  );
};

export default Home;