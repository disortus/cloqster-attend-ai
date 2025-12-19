import React, { useEffect, useState } from "react";
import "../Panels/PanelUI.css";

const API = "http://localhost:5000";

export default function TeacherPanel() {
    const [lessons, setLessons] = useState([]);
    const [attends, setAttends] = useState([]);
    const [lessonId, setLessonId] = useState(null);

    useEffect(() => {
        fetch(`${API}/teacher/get_lessons`, { credentials: "include" })
            .then(r => r.json())
            .then(setLessons);
    }, []);

    const load = async (id) => {
        setLessonId(id);
        const res = await fetch(`${API}/teacher/attends/${id}`, {
            credentials: "include",
        });
        if (res.ok) setAttends(await res.json());
    };

    const mark = async (id, status) => {
        await fetch(`${API}/teacher/attends/${id}?new_status=${status}`, {
            method: "PUT",
            credentials: "include",
        });
        load(lessonId);
    };

    return (
        <div className="panel-page">
            <div className="panel-container">
                <div className="panel-head">
                    <h1 className="panel-title">Мұғалім панелі</h1>
                    <div className="panel-subtitle">Қолмен қатысу белгілеу</div>
                </div>

                <div className="pbox">
                    {lessons.map(l => (
                        <button key={l.id} className="pbtn blue" onClick={() => load(l.id)}>
                            {l.subj_name} — {l.group_name}
                        </button>
                    ))}
                </div>

                <div className="pbox">
                    <div className="pbox-title">Қатысу</div>
                    <table className="ptable">
                        <tbody>
                        {attends.map(a => (
                            <tr key={a.id}>
                                <td>{a.fullname}</td>
                                <td><span className={`status ${a.status}`}>{a.status}</span></td>
                                <td>
                                    <button className="pbtn green" onClick={() => mark(a.id,"present")}>Келді</button>
                                    <button className="pbtn red" onClick={() => mark(a.id,"absent")}>Жоқ</button>
                                    <button className="pbtn orange" onClick={() => mark(a.id,"late")}>Кеш</button>
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
