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

export default function AdminDashboard() {
    const navigate = useNavigate();

    const [stats, setStats] = useState(null);
    const [trend, setTrend] = useState([]);
    const [breakdown, setBreakdown] = useState(null);
    const [activity, setActivity] = useState([]);
    const [loading, setLoading] = useState(true);

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

                // если не админ/не авторизован — редирект
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

                // тренд: у тебя список [{lesson_date, percent}]
                setTrend(Array.isArray(t) ? t : []);

                // breakdown: у тебя либо {present:{count,percent}...} либо может быть null
                // нормализуем в плоский формат процентов для PieChart
                const normalizedBreakdown = {
                    present: b?.present?.percent ?? b?.present ?? 0,
                    absent: b?.absent?.percent ?? b?.absent ?? 0,
                    late: b?.late?.percent ?? b?.late ?? 0,
                    excused: b?.excused?.percent ?? b?.excused ?? 0,
                };
                setBreakdown(normalizedBreakdown);

                // overview: у тебя список строк
                setActivity(Array.isArray(a) ? a : []);
            } catch (e) {
                console.error(e);
                if (cancelled) return;

                // дефолты чтобы UI не падал
                setStats(null);
                setTrend([]);
                setBreakdown({ present: 0, absent: 0, late: 0, excused: 0 });
                setActivity([]);
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();

        return () => {
            cancelled = true;
        };
    }, [navigate]);

    if (loading) return <div className="ad-wrap">Жүктелуде...</div>;

    // SAFE OBJECTS (важно для пустой БД/ошибок API)
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
        { name: "Себепті", value: safeBreakdown.excused },
    ];

    const colors = ["#22c55e", "#ef4444", "#f59e0b", "#6366f1"];

    return (
        <div className="ad-wrap">
            <h1>Админ панель</h1>

            {/* CARDS */}
            <div className="ad-cards">
                <Card title="Бүгін келгендер" value={safeStats.present} />
                <Card title="Қатыспағандар" value={safeStats.absent} />
                <Card title="Кешіккендер" value={safeStats.late} />
                <Card title="Қатысу %" value={`${safeStats.attendance_percent}%`} />
                <Card title="Топтар" value={safeStats.groups} />
                <Card title="Студенттер" value={safeStats.students} />
            </div>

            {/* CHARTS */}
            <div className="ad-grid">
                <div className="ad-box">
                    <h3>Қатысу динамикасы</h3>

                    {trend.length === 0 ? (
                        <div style={{ padding: 12, color: "#555" }}>Дерек жоқ</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={260}>
                            <LineChart data={trend}>
                                <XAxis dataKey="lesson_date" />
                                <YAxis domain={[0, 100]} />
                                <Tooltip />
                                <Line dataKey="percent" strokeWidth={2} dot />
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

            {/* TABLE */}
            <div className="ad-box">
                <h3>Соңғы іс-әрекеттер</h3>

                {activity.length === 0 ? (
                    <div style={{ padding: 12, color: "#555" }}>Дерек жоқ</div>
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
                                <td>{a.fullname ?? "-"}</td>
                                <td>{a.group_name ?? "-"}</td>
                                <td>{a.status ?? "-"}</td>
                                <td>{a.come_at ? String(a.come_at).slice(11, 16) : "-"}</td>
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
