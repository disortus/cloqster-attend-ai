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

const API = "http://localhost:5000";

const AdminPanel = () => {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState("dashboard");

  // Дашборд
  const [stats, setStats] = useState(null);
  const [trend, setTrend] = useState([]);
  const [breakdown, setBreakdown] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  // Пользователи
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({
    fullName: '',
    email: '',
    password: '',
    role: 'student'
  });
  const [showAddUserForm, setShowAddUserForm] = useState(false);

  // Формы для других данных
  const [groupForm, setGroupForm] = useState({ group_name: '', curator_id: '' });
  const [subjectForm, setSubjectForm] = useState({ subject_name: '', teacher_id: '' });
  const [audForm, setAudForm] = useState({ aud_name: '' });
  const [scheduleForm, setScheduleForm] = useState({
    group_id: '',
    subject_id: '',
    aud_id: '',
    teacher_id: '',
    day_of_week: '',
    start_time: '',
    end_time: ''
  });

  // Для удаления (пример)
  const [deleteGroupId, setDeleteGroupId] = useState('');

  useEffect(() => {
    let cancelled = false;

    const loadDashboard = async () => {
      setLoading(true);
      try {
        const [sRes, tRes, bRes, aRes] = await Promise.all([
          fetch(`${API}/admin/dashboard_stats`, { credentials: "include" }),
          fetch(`${API}/admin/attendance_report`, { credentials: "include" }),
          fetch(`${API}/admin/performance_report`, { credentials: "include" }),
          fetch(`${API}/admin/dashbord_overview`, { credentials: "include" }),
        ]);

        if ([sRes, tRes, bRes, aRes].some(r => r.status === 401 || r.status === 403)) {
          navigate("/login");
          return;
        }

        const s = sRes.ok ? await sRes.json() : null;
        const t = tRes.ok ? await tRes.json() : [];
        const b = bRes.ok ? await bRes.json() : null;
        const a = aRes.ok ? await aRes.json() : [];

        if (!cancelled) {
          setStats(s);
          setTrend(Array.isArray(t) ? t : []);
          setBreakdown({
            present: b?.present?.percent ?? 0,
            absent: b?.absent?.percent ?? 0,
            late: b?.late?.percent ?? 0,
            excused: b?.excused?.percent ?? 0,
          });
          setActivity(Array.isArray(a) ? a : []);
        }
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    const loadUsers = async () => {
      try {
        const [stdRes, teachRes, curRes, adminRes] = await Promise.all([
          fetch(`${API}/admin/get_student`, { credentials: "include" }),
          fetch(`${API}/admin/get_teacher`, { credentials: "include" }),
          fetch(`${API}/admin/get_curator`, { credentials: "include" }),
          fetch(`${API}/admin/get_admin`, { credentials: "include" }),
        ]);

        const students = stdRes.ok ? await stdRes.json() : [];
        const teachers = teachRes.ok ? await teachRes.json() : [];
        const curators = curRes.ok ? await curRes.json() : [];
        const admins = adminRes.ok ? await adminRes.json() : [];

        const allUsers = [
          ...students.map(u => ({ ...u, role: 'student' })),
          ...teachers.map(u => ({ ...u, role: 'teacher' })),
          ...curators.map(u => ({ ...u, role: 'curator' })),
          ...admins.map(u => ({ ...u, role: 'admin' })),
        ];

        setUsers(allUsers);
      } catch (e) {
        console.error(e);
        setUsers([]);
      }
    };

    loadDashboard();
    loadUsers();

    return () => { cancelled = true; };
  }, [navigate]);

  // Добавление пользователя
  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/admin/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          full_name: newUser.fullName,
          email: newUser.email,
          password: newUser.password,
          role: newUser.role
        })
      });

      if (res.ok) {
        alert("Пайдаланушы қосылды!");
        setNewUser({ fullName: '', email: '', password: '', role: 'student' });
        setShowAddUserForm(false);
      } else {
        alert("Қате: " + await res.text());
      }
    } catch (e) {
      alert("Сервер қатесі");
    }
  };

  // Удаление пользователя
  const handleDeleteUser = async (id) => {
    if (!window.confirm("Бұл пайдаланушыны өшіргіңіз келеді ме?")) return;

    try {
      const res = await fetch(`${API}/admin/delete_user`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ user_id: id })
      });

      if (res.ok) {
        setUsers(users.filter(u => u.id !== id));
        alert("Пайдаланушы өшірілді!");
      } else {
        alert("Қате: " + await res.text());
      }
    } catch (e) {
      alert("Сервер қатесі");
    }
  };

  // Добавление группы
  const handleAddGroup = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/admin/groups`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(groupForm)
      });
      if (res.ok) {
        alert("Топ қосылды!");
        setGroupForm({ group_name: '', curator_id: '' });
      } else {
        alert("Қате");
      }
    } catch (e) {
      alert("Сервер қатесі");
    }
  };

  // Добавление предмета
  const handleAddSubject = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/admin/add_subject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(subjectForm)
      });
      if (res.ok) {
        alert("Пән қосылды!");
        setSubjectForm({ subject_name: '', teacher_id: '' });
      } else {
        alert("Қате");
      }
    } catch (e) {
      alert("Сервер қатесі");
    }
  };

  // Добавление аудитории
  const handleAddAud = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/admin/add_audience`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(audForm)
      });
      if (res.ok) {
        alert("Аудитория қосылды!");
        setAudForm({ aud_name: '' });
      } else {
        alert("Қате");
      }
    } catch (e) {
      alert("Сервер қатесі");
    }
  };

  // Добавление расписания
  const handleAddSchedule = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/admin/add_schedule`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(scheduleForm)
      });
      if (res.ok) {
        alert("Сабақ қосылды!");
        setScheduleForm({
          group_id: '',
          subject_id: '',
          aud_id: '',
          teacher_id: '',
          day_of_week: '',
          start_time: '',
          end_time: ''
        });
      } else {
        alert("Қате");
      }
    } catch (e) {
      alert("Сервер қатесі");
    }
  };

  // Удаление группы (пример)
  const handleDeleteGroup = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/admin/delete_group`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ group_id: deleteGroupId })
      });
      if (res.ok) {
        alert("Топ өшірілді!");
        setDeleteGroupId('');
      } else {
        alert("Қате");
      }
    } catch (e) {
      alert("Сервер қатесі");
    }
  };

  if (loading) return <div className="admin-loading">Жүктелуде...</div>;

  const safeStats = stats ?? { present: 0, absent: 0, late: 0, attendance_percent: 0, groups: 0, students: 0 };
  const safeBreakdown = breakdown ?? { present: 0, absent: 0, late: 0, excused: 0 };

  const pieData = [
    { name: "Келді", value: safeBreakdown.present },
    { name: "Қатыспады", value: safeBreakdown.absent },
    { name: "Кешікті", value: safeBreakdown.late },
  ];

  const COLORS = ["#28a745", "#dc3545", "#fd7e14"];

  return (
    <div className="admin-panel">
      <h1 className="admin-title">Әкімші Панелі</h1>

      <div className="admin-tabs">
        <button className={activeTab === 'dashboard' ? 'tab-active' : 'tab'} onClick={() => setActiveTab('dashboard')}>
          Статистика мен тіркеу
        </button>
        <button className={activeTab === 'data' ? 'tab-active' : 'tab'} onClick={() => setActiveTab('data')}>
          Деректерді басқару
        </button>
      </div>

      {activeTab === 'dashboard' && (
        <>
          <div className="stats-grid">
            <StatCard title="Бүгін келгендер" value={safeStats.present} color="#28a745" />
            <StatCard title="Қатыспағандар" value={safeStats.absent} color="#dc3545" />
            <StatCard title="Кешіккендер" value={safeStats.late} color="#fd7e14" />
            <StatCard title="Қатысу пайызы" value={`${safeStats.attendance_percent}%`} color="#007bff" />
            <StatCard title="Топтар саны" value={safeStats.groups} color="#6f42c1" />
            <StatCard title="Студенттер саны" value={safeStats.students} color="#17a2b8" />
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h3>Қатысу динамикасы</h3>
              {trend.length === 0 ? <p className="no-data">Дерек жоқ</p> : (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trend}>
                    <XAxis dataKey="lesson_date" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip formatter={(v) => `${v}%`} />
                    <Line type="monotone" dataKey="percent" stroke="#007bff" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="chart-card">
              <h3>Бүгінгі қатысу</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" cx="50%" cy="50%" innerRadius={60} outerRadius={100}>
                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                  </Pie>
                  <Tooltip formatter={(v) => `${v}%`} />
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

          <div className="activity-card">
            <h3>Соңғы іс-әрекеттер</h3>
            {activity.length === 0 ? <p className="no-data">Дерек жоқ</p> : (
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
                    {activity.map((item, i) => (
                      <tr key={i}>
                        <td>{item.fullname || '-'}</td>
                        <td>{item.group_name || '-'}</td>
                        <td className={`status-cell ${item.status?.toLowerCase() || ''}`}>{item.status || '-'}</td>
                        <td>{item.come_at ? item.come_at.slice(11, 16) : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Управление пользователями */}
          <div className="users-section">
            <h3>Пайдаланушыларды басқару ({users.length})</h3>
            <button className="add-user-btn" onClick={() => setShowAddUserForm(!showAddUserForm)}>
              {showAddUserForm ? 'Жабу' : 'Жаңа пайдаланушы қосу'}
            </button>

            {showAddUserForm && (
              <div className="add-user-form">
                <form onSubmit={handleAddUser}>
                  <input type="text" placeholder="Аты-жөні" value={newUser.fullName}
                    onChange={e => setNewUser({...newUser, fullName: e.target.value})} required />
                  <input type="email" placeholder="Email (логин)" value={newUser.email}
                    onChange={e => setNewUser({...newUser, email: e.target.value})} required />
                  <input type="password" placeholder="Құпия сөз" value={newUser.password}
                    onChange={e => setNewUser({...newUser, password: e.target.value})} required />
                  <select value={newUser.role} onChange={e => setNewUser({...newUser, role: e.target.value})}>
                    <option value="student">Студент</option>
                    <option value="teacher">Мұғалім</option>
                    <option value="curator">Куратор</option>
                    <option value="admin">Әкімші</option>
                  </select>
                  <div className="form-buttons">
                    <button type="submit" className="save-btn">Қосу</button>
                    <button type="button" onClick={() => setShowAddUserForm(false)} className="cancel-btn">Бас тарту</button>
                  </div>
                </form>
              </div>
            )}

            <div className="table-wrapper">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Аты-жөні</th>
                    <th>Email</th>
                    <th>Рөл</th>
                    <th>Әрекет</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.full_name || user.fullName || '-'}</td>
                      <td>{user.email}</td>
                      <td>{
                        user.role === 'student' ? 'Студент' :
                        user.role === 'teacher' ? 'Мұғалім' :
                        user.role === 'curator' ? 'Куратор' :
                        'Әкімші'
                      }</td>
                      <td>
                        <button className="delete-btn" onClick={() => handleDeleteUser(user.id)}>Өшіру</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {activeTab === 'data' && (
        <div className="data-management">
          <h2>Басқа деректерді басқару</h2>

          <div className="admin-form">
            <h3>Топ қосу</h3>
            <form onSubmit={handleAddGroup}>
              <input placeholder="Топ атауы" value={groupForm.group_name} onChange={e => setGroupForm({...groupForm, group_name: e.target.value})} required />
              <input placeholder="Куратор ID" value={groupForm.curator_id} onChange={e => setGroupForm({...groupForm, curator_id: e.target.value})} />
              <button type="submit">Топ қосу</button>
            </form>
          </div>

          <div className="admin-form">
            <h3>Пән қосу</h3>
            <form onSubmit={handleAddSubject}>
              <input placeholder="Пән атауы" value={subjectForm.subject_name} onChange={e => setSubjectForm({...subjectForm, subject_name: e.target.value})} required />
              <input placeholder="Мұғалім ID" value={subjectForm.teacher_id} onChange={e => setSubjectForm({...subjectForm, teacher_id: e.target.value})} />
              <button type="submit">Пән қосу</button>
            </form>
          </div>

          <div className="admin-form">
            <h3>Аудитория қосу</h3>
            <form onSubmit={handleAddAud}>
              <input placeholder="Аудитория атауы" value={audForm.aud_name} onChange={e => setAudForm({...audForm, aud_name: e.target.value})} required />
              <button type="submit">Аудитория қосу</button>
            </form>
          </div>

          <div className="admin-form">
            <h3>Сабақ қосу (расписание)</h3>
            <form onSubmit={handleAddSchedule}>
              <input placeholder="Топ ID" value={scheduleForm.group_id} onChange={e => setScheduleForm({...scheduleForm, group_id: e.target.value})} required />
              <input placeholder="Пән ID" value={scheduleForm.subject_id} onChange={e => setScheduleForm({...scheduleForm, subject_id: e.target.value})} required />
              <input placeholder="Аудитория ID" value={scheduleForm.aud_id} onChange={e => setScheduleForm({...scheduleForm, aud_id: e.target.value})} required />
              <input placeholder="Мұғалім ID" value={scheduleForm.teacher_id} onChange={e => setScheduleForm({...scheduleForm, teacher_id: e.target.value})} required />
              <input placeholder="Күн (1-7)" value={scheduleForm.day_of_week} onChange={e => setScheduleForm({...scheduleForm, day_of_week: e.target.value})} required />
              <input placeholder="Басталу (HH:MM)" value={scheduleForm.start_time} onChange={e => setScheduleForm({...scheduleForm, start_time: e.target.value})} required />
              <input placeholder="Аяқталу (HH:MM)" value={scheduleForm.end_time} onChange={e => setScheduleForm({...scheduleForm, end_time: e.target.value})} required />
              <button type="submit">Сабақ қосу</button>
            </form>
          </div>

          <div className="admin-form">
            <h3>Өшіру (топ мысалы)</h3>
            <form onSubmit={handleDeleteGroup}>
              <input placeholder="Топ ID" value={deleteGroupId} onChange={e => setDeleteGroupId(e.target.value)} required />
              <button type="submit">Топ өшіру</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ title, value, color }) => (
  <div className="stat-card" style={{ borderLeft: `5px solid ${color}` }}>
    <p className="stat-title">{title}</p>
    <p className="stat-value" style={{ color }}>{value}</p>
  </div>
);

export default AdminPanel;