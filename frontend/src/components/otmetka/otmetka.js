import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './otmetka.css';

const Otmetka = () => {
  // Данные студента (потом можно из контекста или бэка брать)
  const studentName = "Алигожин Ерасыл";

  // Текущий статус и время (заглушка)
  const currentStatus = "Келді"; // Можно динамически менять
  const currentTime = new Date().toLocaleTimeString('kk-KZ', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });

  // История посещений (заглушка)
  const attendanceHistory = [
    { date: '2025-12-18', timeIn: '08:45', timeOut: '17:30', status: 'Келді' },
    { date: '2025-12-17', timeIn: '09:05', timeOut: '17:20', status: 'Кешікті' },
    { date: '2025-12-16', timeIn: '08:50', timeOut: '17:35', status: 'Келді' },
    { date: '2025-12-15', timeIn: '-', timeOut: '-', status: 'Болмады' },
    { date: '2025-12-14', timeIn: '08:30', timeOut: '17:15', status: 'Келді' },
  ];

  const [showCamera, setShowCamera] = useState(false);

  const getStatusClass = (status) => {
    if (status === 'Келді') return 'green';
    if (status === 'Кешікті') return 'orange';
    return 'red';
  };

  return (
    <div className="otmetka-panel">
      {/* Приветствие */}
      <div className="panel-header">
        <h1>Сәлем, {studentName}!</h1>
        <p className="today-date">
          Бүгін: {new Date().toLocaleDateString('kk-KZ', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </p>
      </div>

      {/* Карточка текущего статуса */}
      <div className="status-card">
        <div className="status-info">
          <h2>Бүгінгі статус</h2>
          <p className={`status ${getStatusClass(currentStatus)}`}>
            {currentStatus}
          </p>
          <p className="time-info">Келу уақыты: {currentTime}</p>
        </div>

        <button
          className="mark-btn"
          onClick={() => setShowCamera(true)}
        >
          Қазір Белгі Қою
        </button>
      </div>

      {/* Модальное окно с камерой */}
      {showCamera && (
        <div className="camera-modal" onClick={() => setShowCamera(false)}>
          <div className="camera-content" onClick={(e) => e.stopPropagation()}>
            <h2>Белгі қою</h2>
            <div className="camera-placeholder">
              <p role="img" aria-label="camera">📷</p>
              <p>Камера жүктелуде...</p>
              <small>(Кейін нақты камера қосылады: getUserMedia + Face API)</small>
            </div>
            <button
              onClick={() => setShowCamera(false)}
              className="close-btn"
            >
              Жабу
            </button>
          </div>
        </div>
      )}

      {/* История посещений */}
      <div className="history-section">
        <h2>Соңғы белгілер</h2>
        <div className="table-container">
          <table className="history-table">
            <thead>
              <tr>
                <th>Күн</th>
                <th>Келу</th>
                <th>Кету</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              {attendanceHistory.map((day, index) => (
                <tr key={index}>
                  <td>{day.date}</td>
                  <td>{day.timeIn}</td>
                  <td>{day.timeOut}</td>
                  <td className={getStatusClass(day.status)}>
                    {day.status}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Навигация */}
      <div className="panel-footer">
        <Link to="/" className="back-link">Басты бетке оралу</Link>
      </div>
    </div>
  );
};

export default Otmetka;