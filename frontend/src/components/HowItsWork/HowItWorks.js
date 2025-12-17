import React, { useEffect } from 'react';
import './HowItWorks.css';  // ← правильный импорт

const HowItWorks = () => {
  useEffect(() => {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
      setTimeout(() => {
        step.classList.add('active');
      }, 400 + index * 1000);
    });
  }, []);

  return (
    <div className="how-container">
      <h1 className="title">Қалай жұмыс істейді</h1>
      <p className="subtitle">
        Барлығы бірнеше секундта орындалады, қосымша ештеңе орнатуды қажет етпейді :p.
      </p>

      <div className="steps">
        <div className="step" data-step="1">
          <div className="step-number">1</div>
          <div className="step-content">
            <h3 className="step-title">Камераға рұқсат беру</h3>
            <p className="step-desc">Қорықпаңыз, бұл тек бетіңізді тану үшін қажет.</p>
          </div>
          <div className="check-icon">✔</div>
        </div>

        <div className="step" data-step="2">
          <div className="step-number">2</div>
          <div className="step-content">
            <h3 className="step-title">Жүйе бетіңізді таниды және уақытты белгілейді</h3>
            <p className="step-desc">Автоматты түрде біздің база арқылы анықталады</p>
          </div>
          <div className="check-icon">✔</div>
        </div>

        <div className="step" data-step="3">
          <div className="step-number">3</div>
          <div className="step-content">
            <h3 className="step-title">Уақытыңда келгеніңізді/кешіккеніңізді анықтайды</h3>
            <p className="step-desc">Бәрін жеке студент панелінде көре аласыз!</p>
          </div>
          <div className="check-icon">✔</div>
        </div>

        <div className="step" data-step="4">
          <div className="step-number">4</div>
          <div className="step-content">
            <h3 className="step-title">Нәтижені естелікте сақтайды</h3>
            <p className="step-desc">Барлық деректер сақталып қалады, уайымдамаңыз</p>
          </div>
          <div className="check-icon">✔</div>
        </div>
      </div>
    </div>
  );
};

export default HowItWorks;