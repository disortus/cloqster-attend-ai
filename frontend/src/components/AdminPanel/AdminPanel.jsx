import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import "./AdminPanel.css";

const API = "http://localhost:5000";  // Бэкенд API

const AdminPanel = () => {
  const navigate = useNavigate();

  // Состояние для статистики и графиков
  const [stats, setStats] = useState(null);
  const [trend, setTrend] = useState([]);
  const [breakdown, setBreakdown] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  // Состояние для пользователей
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({
    fullName: '',
    email: '',
    password: '',
    role: 'student'
  });
  const [showAddForm, setShowAddForm] = useState(false);
  const [usersLoading, setUsersLoading] = useState(true);

  // Загрузка статистики и графиков
  useEffect(() => {
    let cancelled = false;

    (async () => {
      setLoading(true);

      try {
        const [sRes, tRes, bRes, aRes] = await Promise.all([
          fetch(`${API}/admin/dashboard_stats`, { credentials: "include" }),
          fetch(`${API}/admin/attendance_report`, { credentials: "include" }),
          fetch(`${API}/admin/performance_report`, { credentials: "include" }),
          fetch(`${API}/admin/dashboard_overview`, { credentials: "include" }),
        ]);

        if ([sRes, tRes, bRes, aRes].some((r) => r.status === 401 || r.status === 403)) {
          navigate("/login");
          return;
        }

        const s = sRes.ok ? await sRes.json() : null;
        const t = tRes.ok ? await tRes.json() : [];
        const b = bRes.ok ? await bRes.json() : null;
        const a = aRes.ok ? await aRes.json() : [];

        if (cancelled) return;

        setStats(s);
        setTrend(Array.isArray(t) ? t : []);

        const normalizedBreakdown = {
          present: b?.present?.percent ?? b?.present ?? 0,
          absent: b?.absent?.percent ?? b?.absent ?? 0,
          late: b?.late?.percent ?? b?.late ?? 0,
          excused: b?.excused?.percent ?? b?.excused ?? 0,
        };
        setBreakdown(normalizedBreakdown);

        setActivity(Array.isArray(a) ? a : []);
      } catch (e) {
        console.error(e);
        if (cancelled) return;

        setStats(null);
        setTrend([]);
        setBreakdown({ present: 0, absent: 0, late: 0, excused: 0 });
        setActivity([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    // Загрузка списка пользователей (новый запрос)
    (async () => {
      setUsersLoading(true);
      try {
        const uRes = await fetch(`${API}/admin/users`, { credentials: "include" });
        if (uRes.status === 401 || uRes.status === 403) {
          navigate("/login");
          return;
        }
        const uData = uRes.ok ? await uRes.json() : [];
        setUsers(Array.isArray(uData) ? uData : []);
      } catch (e) {
        console.error(e);
        setUsers([]);
      } finally {
        setUsersLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [navigate]);

  if (loading || usersLoading) {
    return <div className="admin-loading">Жүктелуде...</div>;
  }

  // Безопасные значения для статистики
  const safeStats = stats ?? {
    present: 0,
    absent: 0,
    late: 0,
    attendance_percent: 0,
    groups: 0,
    students: 0,
  };

  const safeBreakdown = breakdown ?? { present: 0, absent: 0, late: 0, excused: 0 };

  const pieData = [
    { name: "Келді", value: safeBreakdown.present },
    { name: "Қатыспады", value: safeBreakdown.absent },
    { name: "Кешікті", value: safeBreakdown.late },
  ];

  const COLORS = ["#28a745", "#dc3545", "#fd7e14"];

  // Функции для пользователей
  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API}/admin/add_user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: "include",
        body: JSON.stringify(newUser)
      });
      if (response.ok) {
        const addedUser = await response.json();
        setUsers([...users, addedUser]);
        setNewUser({ fullName: '', email: '', password: '', role: 'student' });
        setShowAddForm(false);
        alert('Жаңа пайдаланушы қосылды!\nЛогин: ' + newUser.email + '\nҚұпия сөз: ' + newUser.password);
      } else {
        alert('Қате: ' + (await response.text()));
      }
    } catch (e) {
      console.error(e);
      alert('Сервер қатесі');
    }
  };

  const handleDeleteUser = async (id) => {
    if (window.confirm('Өшіруге сенімдісіз бе?')) {
      try {
        const response = await fetch(`${API}/admin/delete_user/${id}`, {
          method: 'DELETE',
          credentials: "include"
        });
        if (response.ok) {
          setUsers(users.filter(user => user.id !== id));
        } else {
          alert('Қате: ' + (await response.text()));
        }
      } catch (e) {
        console.error(e);
        alert('Сервер қатесі');
      }
    }
  };

  return (
    <div className="admin-panel">
      <h1 className="admin-title">Әкімші Панелі</h1>

      {/* Карточки статистики */}
      <div className="stats-grid">
        <StatCard title="Бүгін келгендер" value={safeStats.present} color="#28a745" />
        <StatCard title="Қатыспағандар" value={safeStats.absent} color="#dc3545" />
        <StatCard title="Кешіккендер" value={safeStats.late} color="#fd7e14" />
        <StatCard title="Қатысу пайызы" value={`${safeStats.attendance_percent}%`} color="#007bff" />
        <StatCard title="Топтар саны" value={safeStats.groups} color="#6f42c1" />
        <StatCard title="Студенттер саны" value={safeStats.students} color="#17a2b8" />
      </div>

      {/* Графики */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Қатысу динамикасы</h3>
          {trend.length === 0 ? (
            <p className="no-data">Деректер жоқ</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trend}>
                <XAxis dataKey="lesson_date" />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(value) => `${value}%`} />
                <Line type="monotone" dataKey="percent" stroke="#007bff" strokeWidth={3} dot={{ fill: '#007bff' }} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="chart-card">
          <h3>Бүгінгі қатысу</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value}%`} />
            </PieChart>
          </ResponsiveContainer>
          <div className="pie-legend">
            {pieData.map((item, i) => (
              <div key={i} className="legend-item">
                <span className="legend-color" style={{ backgroundColor: COLORS[i] }}></span>
                <span>{item.name}: {item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Таблица активности */}
      <div className="chart-card">
        <h3>Соңғы іс-әрекеттер</h3>
        {activity.length === 0 ? (
          <p className="no-data">Деректер жоқ</p>
        ) : (
          <div className="table-wrapper">
            <table className="activity-table">
              <thead>
                <tr>
                  <th>Студент</th>
                  <th>Топ</th>
                  <th>Статус</th>
                  <th>Уақыт</th>
                </tr>
              </thead>
              <tbody>
                {activity.map((item, index) => (
                  <tr key={index}>
                    <td>{item.fullname || '-'}</td>
                    <td>{item.group_name || '-'}</td>
                    <td className={`status-cell ${item.status?.toLowerCase() || ''}`}>
                      {item.status || '-'}
                    </td>
                    <td>{item.come_at ? item.come_at.slice(11, 16) : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Раздел управления пользователями */}
      <div className="users-section">
        <h3>Пайдаланушыларды басқару</h3>

        <div className="admin-actions">
          <button 
            className="add-user-btn"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? 'Жабу' : 'Жаңа пайдаланушы қосу'}
          </button>
        </div>

        {showAddForm && (
          <div className="add-user-form">
            <h4>Жаңа пайдаланушы</h4>
            <form onSubmit={handleAddUser}>
              <input
                type="text"
                placeholder="Аты-жөні"
                value={newUser.fullName}
                onChange={(e) => setNewUser({...newUser, fullName: e.target.value})}
                required
              />
              <input
                type="email"
                placeholder="Email (логин)"
                value={newUser.email}
                onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                required
              />
              <input
                type="password"
                placeholder="Құпия сөз"
                value={newUser.password}
                onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                required
              />
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({...newUser, role: e.target.value})}
              >
                <option value="student">Студент</option>
                <option value="teacher">Мұғалім</option>
                <option value="admin">Әкімші</option>
                <option value="curator">Куратор</option>
              </select>
              <div className="form-buttons">
                <button type="submit" className="save-btn">Қосу</button>
                <button type="button" onClick={() => setShowAddForm(false)} className="cancel-btn">Бас тарту</button>
              </div>
            </form>
          </div>
        )}

        {/* Таблица пользователей */}
        <div className="users-table-wrapper">
          <h4>Пайдаланушылар ({users.length})</h4>
          <table className="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Аты-жөні</th>
                <th>Email</th>
                <th>Рөл</th>
                <th>Статус</th>
                <th>Әрекет</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.fullName}</td>
                  <td>{user.email}</td>
                  <td>{user.role === 'student' ? 'Студент' : user.role === 'teacher' ? 'Мұғалім' : 'Әкімші'}</td>
                  <td className={user.status === 'active' ? 'green' : 'red'}>{user.status === 'active' ? 'Белсенді' : 'Белсенді емес'}</td>
                  <td>
                    <button className="delete-btn" onClick={() => handleDeleteUser(user.id)}>Өшіру</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Компонент карточки
const StatCard = ({ title, value, color }) => (
  <div className="stat-card" style={{ borderLeft: `5px solid ${color}` }}>
    <p className="stat-title">{title}</p>
    <p className="stat-value" style={{ color }}>{value}</p>
  </div>
);

export default AdminPanel;