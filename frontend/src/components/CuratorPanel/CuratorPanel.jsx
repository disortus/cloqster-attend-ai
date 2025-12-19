import React, { useState } from "react";
import "../Panels/PanelUI.css";

const API = "http://localhost:5000";

export default function CuratorPanel() {
    const [groupId, setGroupId] = useState("");
    const [attends, setAttends] = useState([]);

    const load = async () => {
        const res = await fetch(`${API}/curator/attends/${groupId}`, {
            credentials: "include",
        });
        if (res.ok) setAttends(await res.json());
    };

    const update = async (id, status) => {
        await fetch(`${API}/curator/attends/${id}?new_status=${status}`, {
            method: "PUT",
            credentials: "include",
        });
        load();
    };

    return (
        <div className="panel-page">
            <div className="panel-container">
                <div className="panel-head">
                    <h1 className="panel-title">Куратор панелі</h1>
                    <div className="panel-subtitle">Өз тобының қатысуын бақылау</div>
                </div>

                <div className="pbox">
                    <input
                        placeholder="Group ID"
                        value={groupId}
                        onChange={e => setGroupId(e.target.value)}
                    />
                    <button className="pbtn blue" onClick={load}>Жүктеу</button>
                </div>

                <div className="pbox">
                    <div className="pbox-title">Студенттер</div>
                    <table className="ptable">
                        <thead>
                        <tr>
                            <th>Аты</th>
                            <th>Статус</th>
                            <th>Өзгерту</th>
                        </tr>
                        </thead>
                        <tbody>
                        {attends.map(a => (
                            <tr key={a.id}>
                                <td>{a.fullname}</td>
                                <td><span className={`status ${a.status}`}>{a.status}</span></td>
                                <td>
                                    <button className="pbtn green" onClick={() => update(a.id,"present")}>Келді</button>
                                    <button className="pbtn red" onClick={() => update(a.id,"absent")}>Жоқ</button>
                                    <button className="pbtn orange" onClick={() => update(a.id,"late")}>Кеш</button>
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
