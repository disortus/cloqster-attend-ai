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
        fullname: "",
        email: "",
        password: "",
        role: "student",
    });
    const [showAddUserForm, setShowAddUserForm] = useState(false);

    // --- dashboard загрузка ---
    useEffect(() => {
        let cancelled = false;

        const loadDashboard = async () => {
            setLoading(true);

            try {
                const [sRes, tRes, bRes, aRes] = await Promise.all([
                    fetch(`${API}/admin/dashboard_stats`, { credentials: "include" }),
                    fetch(`${API}/admin/attendance_report`, { credentials: "include" }),
                    fetch(`${API}/admin/performance_report`, { credentials: "include" }),
                    // у тебя реально endpoint с опечаткой:
                    fetch(`${API}/admin/dashbord_overview`, { credentials: "include" }),
                ]);

                if ([sRes, tRes, bRes, aRes].some((r) => r.status === 401 || r.status === 403)) {
                    navigate("/login");
                    return;
                }

                const s = sRes.ok ? await sRes.json() : null;
                const t = tRes.ok ? await tRes.json() : [];
                const b = bRes.ok ? await bRes.json() : null;
                const a = aRes.ok ? await aRes.json() : { items: [] };

                if (cancelled) return;

                // ✅ МАППИНГ stats под твой бэк
                // бэк: today_present/today_absent/... groups_count/students_count
                const mappedStats = s
                    ? {
                        present: s.today_present ?? 0,
                        absent: s.today_absent ?? 0,
                        late: s.today_late ?? 0,
                        attendance_percent: s.attendance_percent ?? 0,
                        groups: s.groups_count ?? 0,
                        students: s.students_count ?? 0,
                    }
                    : null;

                setStats(mappedStats);

                // trend = список [{lesson_date, percent}]
                setTrend(Array.isArray(t) ? t : []);

                // ✅ breakdown под твой бэк (он возвращает числа percent)
                // { present: 80, absent: 10, late: 10 }
                setBreakdown({
                    present: b?.present ?? 0,
                    absent: b?.absent ?? 0,
                    late: b?.late ?? 0,
                    excused: b?.excused ?? 0,
                });

                // ✅ activity под твой бэк (мы сделали dict {items: []})
                setActivity(Array.isArray(a?.items) ? a.items : []);
            } catch (e) {
                console.error(e);
                if (!cancelled) {
                    setStats(null);
                    setTrend([]);
                    setBreakdown({ present: 0, absent: 0, late: 0, excused: 0 });
                    setActivity([]);
                }
            } finally {
                if (!cancelled) setLoading(false);
            }
        };

        const loadUsers = async () => {
            try {
                const res = await fetch(`${API}/admin/users`, { credentials: "include" });
                if (!res.ok) {
                    setUsers([]);
                    return;
                }
                const data = await res.json();
                setUsers(Array.isArray(data) ? data : []);
            } catch (e) {
                console.error(e);
                setUsers([]);
            }
        };

        loadDashboard();
        loadUsers();

        return () => {
            cancelled = true;
        };
    }, [navigate]);

    // --- users: add ---
    const handleAddUser = async (e) => {
        e.preventDefault();

        try {
            const res = await fetch(`${API}/admin/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    email: newUser.email,
                    password: newUser.password,
                    role: newUser.role,
                    fullname: newUser.fullname, // ✅ важно: fullname (как в schema)
                }),
            });

            if (res.ok) {
                alert("Пайдаланушы қосылды!");
                setNewUser({ fullname: "", email: "", password: "", role: "student" });
                setShowAddUserForm(false);

                // перезагрузить список
                const uRes = await fetch(`${API}/admin/users`, { credentials: "include" });
                const uData = uRes.ok ? await uRes.json() : [];
                setUsers(Array.isArray(uData) ? uData : []);
            } else {
                alert("Қате: " + (await res.text()));
            }
        } catch (e) {
            alert("Сервер қатесі");
        }
    };

    // --- users: delete (у тебя удаление по email!) ---
    const handleDeleteUser = async (email) => {
        if (!window.confirm("Бұл пайдаланушыны өшіргіңіз келеді ме?")) return;

        try {
            const res = await fetch(`${API}/admin/delete_user`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ email }), // ✅ важно: email
            });

            if (res.ok) {
                setUsers((prev) => prev.filter((u) => u.email !== email));
                alert("Пайдаланушы өшірілді!");
            } else {
                alert("Қате: " + (await res.text()));
            }
        } catch (e) {
            alert("Сервер қатесі");
        }
    };

    if (loading) return <div className="admin-loading">Жүктелуде...</div>;

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

    return (
        <div className="admin-panel">
            <h1 className="admin-title">Әкімші Панелі</h1>

            <div className="admin-tabs">
                <button
                    className={activeTab === "dashboard" ? "tab-active" : "tab"}
                    onClick={() => setActiveTab("dashboard")}
                >
                    Статистика мен тіркеу
                </button>
                <button
                    className={activeTab === "data" ? "tab-active" : "tab"}
                    onClick={() => setActiveTab("data")}
                >
                    Деректерді басқару
                </button>
            </div>

            {activeTab === "dashboard" && (
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
                            {trend.length === 0 ? (
                                <p className="no-data">Дерек жоқ</p>
                            ) : (
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
                                        {pieData.map((_, i) => (
                                            <Cell key={i} fill={COLORS[i]} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(v) => `${v}%`} />
                                </PieChart>
                            </ResponsiveContainer>

                            <div className="pie-legend">
                                {pieData.map((item, i) => (
                                    <div key={i} className="legend-item">
                                        <span className="legend-color" style={{ backgroundColor: COLORS[i] }} />
                                        <span>
                      {item.name}: {item.value}%
                    </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="activity-card">
                        <h3>Соңғы іс-әрекеттер</h3>
                        {activity.length === 0 ? (
                            <p className="no-data">Дерек жоқ</p>
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
                                    {activity.map((item, i) => (
                                        <tr key={i}>
                                            <td>{item.student ?? "-"}</td>
                                            <td>{item.group ?? "-"}</td>
                                            <td className={`status-cell ${String(item.status ?? "").toLowerCase()}`}>{item.status ?? "-"}</td>
                                            <td>{item.time ?? "-"}</td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>

                    {/* Users */}
                    <div className="users-section">
                        <h3>Пайдаланушыларды басқару ({users.length})</h3>

                        <button className="add-user-btn" onClick={() => setShowAddUserForm(!showAddUserForm)}>
                            {showAddUserForm ? "Жабу" : "Жаңа пайдаланушы қосу"}
                        </button>

                        {showAddUserForm && (
                            <div className="add-user-form">
                                <form onSubmit={handleAddUser}>
                                    <input
                                        type="text"
                                        placeholder="Аты-жөні"
                                        value={newUser.fullname}
                                        onChange={(e) => setNewUser({ ...newUser, fullname: e.target.value })}
                                        required
                                    />
                                    <input
                                        type="email"
                                        placeholder="Email (логин)"
                                        value={newUser.email}
                                        onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                                        required
                                    />
                                    <input
                                        type="password"
                                        placeholder="Құпия сөз"
                                        value={newUser.password}
                                        onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                                        required
                                    />
                                    <select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}>
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
                                {users.map((u) => (
                                    <tr key={u.id}>
                                        <td>{u.id}</td>
                                        <td>{u.fullname}</td>
                                        <td>{u.email}</td>
                                        <td>{u.role}</td>
                                        <td>
                                            <button className="delete-btn" onClick={() => handleDeleteUser(u.email)}>
                                                Өшіру
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}

            {activeTab === "data" && (
                <div className="data-management">
                    <h2>Басқа деректерді басқару</h2>
                    <p style={{ opacity: 0.7 }}>
                        (Деректерді басқару формаларын сенің нақты схемаларыңа сай бөлек дұрыс жасап шығамыз —
                        қазір дашборд + users толық жұмыс істейді.)
                    </p>
                </div>
            )}
        </div>
    );
};

const StatCard = ({ title, value, color }) => (
    <div className="stat-card" style={{ borderLeft: `5px solid ${color}` }}>
        <p className="stat-title">{title}</p>
        <p className="stat-value" style={{ color }}>
            {value}
        </p>
    </div>
);

export default AdminPanel;
