import React, { useState } from "react";
import { Link } from "react-router-dom";
import './LoginForm.css';
import { MdOutlineEmail, MdLockOutline } from "react-icons/md";

const LoginForm = () => {
    const [login, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const resp = await fetch("http://localhost:8000/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "accept": "application/json"
                },
                body: JSON.stringify({
                    login,
                    password
                })
            });

            if (!resp.ok) {
                const err = await resp.json();
                setError(err.detail || "Қате деректер");
                return;
            }

            const data = await resp.json();
            console.log("Успешный вход:", data);

            // например: сохранить токен
            localStorage.setItem("token", data.access_token);

            // редирект на главную
            window.location.href = "/dashboard";

        } catch (err) {
            console.error("Ошибка:", err);
            setError("Сервер қолжетімсіз", err);
        }
    };

    return (
        <div className="wrapper">
            <form onSubmit={handleSubmit}>
                <h1>Қош келдіңіз!</h1>

                <div className="login-form">
                    <p>Login</p>
                    <div className="input-box">
                        <MdOutlineEmail className="icon" />
                        <input
                            type="text"
                            placeholder="email@example.com"
                            value={login}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <p>Құпия сөз</p>
                    <div className="input-box">
                        <MdLockOutline className="icon" />
                        <input
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {error && <div className="error">{error}</div>}

                    <div className="remember-forgot">
                        <Link to="#">Құпия сөзді ұмыттыңыз ба?</Link>
                    </div>

                    <button type="submit">Кіру</button>
                </div>

                <div className="register-link">
                    <p>Аккаунт жоқ па? <Link to="/register" className="reg">Тіркелу</Link></p>
                </div>
            </form>
        </div>
    );
};

export default LoginForm;
