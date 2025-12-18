import React from 'react';
import './AttendanceHistory.css';

const AttendanceHistory = () => {
  // Заглушка данных (потом берингиз бэкендтен)
  const history = [
    { date: '2025-12-18', timeIn: '08:45', timeOut: '17:30', status: 'Келді' },
    { date: '2025-12-17', timeIn: '09:05', timeOut: '17:20', status: 'Кешікті' },
    { date: '2025-12-16', timeIn: '08:50', timeOut: '17:35', status: 'Келді' },
    { date: '2025-12-15', timeIn: '-', timeOut: '-', status: 'Болмады' },
    { date: '2025-12-14', timeIn: '08:30', timeOut: '17:15', status: 'Келді' },
  ];

  const getStatusClass = (status) => {
    if (status === 'Келді') return 'green';
    if (status === 'Кешікті') return 'orange';
    return 'red';
  };

  return (
    <div className="history-panel">
      <h1 className="history-title">Қатысу тарихы</h1>

      <div className="history-table-container">
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
            {history.map((day, index) => (
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
  );
};

export default AttendanceHistory;