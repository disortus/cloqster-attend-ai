import React, { useEffect, useState } from "react";
import "../Panels/PanelUI.css";

const API = "http://localhost:5000";

export default function StudentPanel() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch(`${API}/student/schedule`, { credentials: "include" })
            .then(r => r.json())
            .then(setData);
    }, []);

    return (
        <div className="panel-page">
            <div className="panel-container">
                <div className="panel-head">
                    <h1 className="panel-title">Студент панелі</h1>
                    <div className="panel-subtitle">Өз қатысу тарихы</div>
                </div>

                <div className="pbox">
                    <table className="ptable">
                        <thead>
                        <tr>
                            <th>Пән</th>
                            <th>Күні</th>
                            <th>Статус</th>
                        </tr>
                        </thead>
                        <tbody>
                        {data.map((d, i) => (
                            <tr key={i}>
                                <td>{d.subj_name}</td>
                                <td>{d.lesson_date}</td>
                                <td><span className={`status ${d.status}`}>{d.status}</span></td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
