import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './StudentPanel.css';

const StudentPanel = () => {
  // Заглушка данных студента
  const studentName = "Алигожин Ерасыл";
  const currentStatus = "Келді";
  const currentTime = new Date().toLocaleTimeString('kk-KZ');

  // Заглушка истории (потом заменишь на данные из бэка)
  const attendanceHistory = [
    { date: '2025-12-18', timeIn: '08:45', timeOut: '17:30', status: 'Келді' },
    { date: '2025-12-17', timeIn: '09:05', timeOut: '17:20', status: 'Кешікті' },
    { date: '2025-12-16', timeIn: '08:50', timeOut: '17:35', status: 'Келді' },
    { date: '2025-12-15', timeIn: '-', timeOut: '-', status: 'Болмады' },
  ];

  const [showCamera, setShowCamera] = useState(false);

  return (
    <div className="student-panel">
      <div className="panel-header">
        <h1>Сәлем, {studentName}!</h1>
        <p>Бүгінгі күн: {new Date().toLocaleDateString('kk-KZ')}</p>
      </div>

      {/* Текущий статус */}
      <div className="status-card">
        <div className="status-info">
          <h2>Қазіргі статус</h2>
          <p className={`status ${currentStatus === 'Келді' ? 'green' : currentStatus === 'Кешікті' ? 'orange' : 'red'}`}>
            {currentStatus}
          </p>
          <p>Келу уақыты: {currentTime}</p>
        </div>
        <button 
          className="mark-btn" 
          onClick={() => setShowCamera(true)}
        >
          Қазір Белгі Қою
        </button>
      </div>

      {/* Заглушка камеры */}
      {showCamera && (
        <div className="camera-modal">
          <div className="camera-content">
            <h2>Камера арқылы белгі қою</h2>
            <div className="camera-placeholder">
              <p>📷 Камера осында ашылады</p>
              <p>(Кейін WebRTC немесе getUserMedia қосамыз)</p>
            </div>
            <button onClick={() => setShowCamera(false)} className="close-btn">
              Жабу
            </button>
          </div>
        </div>
      )}

      {/* История посещений */}
      <div className="history-section">
        <h2>Соңғы белгілер</h2>
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
                <td className={day.status === 'Келді' ? 'green' : day.status === 'Кешікті' ? 'orange' : 'red'}>
                  {day.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Кнопка выхода или назад */}
      <div className="panel-footer">
        <Link to="/" className="back-link">Басты бетке оралу</Link>
      </div>
    </div>
  );
};

export default StudentPanel;