import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./LoginForm.css";
import { MdOutlineEmail, MdLockOutline } from "react-icons/md";

const LoginForm = () => {
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
            const res = await fetch("http://localhost:5000/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email,
                    password,
                }),
            });

            if (!res.ok) {
                const data = await res.json().catch(() => ({}));
                throw new Error(data.message || "Кіру кезінде қате пайда болды");
            }

            const data = await res.json();
            console.log("Успешный вход:", data);

            navigate("/home");
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

                    <div className="remember-forgot">
                        <Link to="#" className="">
                            Құпия сөзді ұмыттыңыз ба?
                        </Link>
                    </div>

                    {error && <p className="error-text">{error}</p>}

                    <button type="submit" disabled={loading}>
                        {loading ? "Кіру..." : "Кіру"}
                    </button>
                </div>
                <div className="register-link">
                    <p>
                        Аккаунт жок па?{" "}
                        <Link to="/register" className="reg">
                            Тіркелу
                        </Link>
                    </p>
                </div>
            </form>
        </div>
    );
};

export default LoginForm;
