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

export default function AdminPanel() {
    const navigate = useNavigate();

    const [stats, setStats] = useState(null);
    const [trend, setTrend] = useState([]);
    const [breakdown, setBreakdown] = useState({ present: 0, absent: 0, late: 0 });
    const [activity, setActivity] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        (async () => {
            try {
                const [sRes, tRes, bRes, aRes] = await Promise.all([
                    fetch(`${API}/admin/dashboard_stats`, { credentials: "include" }),
                    fetch(`${API}/admin/attendance_report`, { credentials: "include" }),
                    fetch(`${API}/admin/performance_report`, { credentials: "include" }),
                    fetch(`${API}/admin/dashbord_overview`, { credentials: "include" }), // ❗ как в бэке
                ]);

                if ([sRes, tRes, bRes, aRes].some(r => r.status === 401 || r.status === 403)) {
                    navigate("/login");
                    return;
                }

                const s = await sRes.json();
                const t = await tRes.json();
                const b = await bRes.json();
                const a = await aRes.json();

                setStats(s);
                setTrend(Array.isArray(t) ? t : []);
                setBreakdown({
                    present: b.present ?? 0,
                    absent: b.absent ?? 0,
                    late: b.late ?? 0,
                });
                setActivity(Array.isArray(a?.items) ? a.items : []);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        })();
    }, [navigate]);

    if (loading) return <div className="ad-wrap">Жүктелуде...</div>;

    const safeStats = stats ?? {
        today_present: 2,
        today_absent: 0,
        today_late: 0,
        attendance_percent: 0,
        groups_count: 0,
        students_count: 0,
    };

    const pieData = [
        { name: "Келді", value: breakdown.present },
        { name: "Қатыспады", value: breakdown.absent },
        { name: "Кешікті", value: breakdown.late },
    ];

    const colors = ["#22c55e", "#ef4444", "#f59e0b"];

    return (
        <div className="ad-wrap">
            <h1>Админ панель</h1>

            <div className="ad-cards">
                <Card title="Бүгін келгендер" value={safeStats.today_present} />
                <Card title="Қатыспағандар" value={safeStats.today_absent} />
                <Card title="Кешіккендер" value={safeStats.today_late} />
                <Card title="Қатысу %" value={`${safeStats.attendance_percent}%`} />
                <Card title="Топтар" value={safeStats.groups_count} />
                <Card title="Студенттер" value={safeStats.students_count} />
            </div>

            <div className="ad-grid">
                <div className="ad-box">
                    <h3>Қатысу динамикасы</h3>
                    {trend.length === 0 ? (
                        <div>Дерек жоқ</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={260}>
                            <LineChart data={trend}>
                                <XAxis dataKey="lesson_date" />
                                <YAxis domain={[0, 100]} />
                                <Tooltip />
                                <Line dataKey="percent" strokeWidth={2} />
                            </LineChart>
                        </ResponsiveContainer>
                    )}
                </div>

                <div className="ad-box">
                    <h3>Бүгінгі қатысу</h3>
                    <ResponsiveContainer width="100%" height={260}>
                        <PieChart>
                            <Pie data={pieData} dataKey="value" innerRadius={60} outerRadius={90}>
                                {pieData.map((_, i) => (
                                    <Cell key={i} fill={colors[i]} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="ad-box">
                <h3>Соңғы іс-әрекеттер</h3>
                {activity.length === 0 ? (
                    <div>Дерек жоқ</div>
                ) : (
                    <table className="ad-table">
                        <thead>
                        <tr>
                            <th>Студент</th>
                            <th>Топ</th>
                            <th>Статус</th>
                            <th>Уақыт</th>
                        </tr>
                        </thead>
                        <tbody>
                        {activity.map((a, i) => (
                            <tr key={i}>
                                <td>{a.student}</td>
                                <td>{a.group}</td>
                                <td>{a.status}</td>
                                <td>{a.time}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

function Card({ title, value }) {
    return (
        <div className="ad-card">
            <div className="ad-card-title">{title}</div>
            <div className="ad-card-value">{value}</div>
        </div>
    );
}
