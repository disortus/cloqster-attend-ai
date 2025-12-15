import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./LoginForm.css";
import { MdOutlineEmail, MdLockOutline } from "react-icons/md";
import { AuthContext } from "../../auth/AuthContext";

const API = "http://localhost:5000";

const LoginForm = () => {
    const { login } = useContext(AuthContext);

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const res = await fetch(`${API}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ email, password }),
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                throw new Error(data.detail || data.message || "Кіру кезінде қате пайда болды");
            }

            // ожидаем { user: {...} }
            const user = data.user ?? data;
            login(user);

            navigate("/home"); // если /home нет — поменяй на нужный роут
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="wrapper">
            <form onSubmit={handleSubmit}>
                <h1>Қош келдіңіз!</h1>

                <div className="login-form">
                    <p>Email</p>
                    <div className="input-box">
                        <MdOutlineEmail className="icon" />
                        <input
                            type="email"
                            placeholder="email@example.com"
                            className="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <p>Құпия сөз</p>
                    <div className="input-box">
                        <MdLockOutline className="icon" />
                        <input
                            type="password"
                            placeholder="••••••••"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>

                    {error && <p className="error-text">{error}</p>}

                    <button type="submit" disabled={loading}>
                        {loading ? "Кіру..." : "Кіру"}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default LoginForm;
