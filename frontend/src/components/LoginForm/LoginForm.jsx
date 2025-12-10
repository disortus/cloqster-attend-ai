import React from "react";
import {Link} from "react-router-dom";
import './LoginForm.css';
import { MdOutlineEmail, MdLockOutline } from "react-icons/md";

const LoginForm = () => {
    return (
        <div className="wrapper">
            <form action="">
                <h1>Қош келдіңіз!</h1>
                <div className="login-form">
                    <p>Email</p>
                    <div className="input-box">
                        <MdOutlineEmail className="icon" />
                        <input type="email" placeholder="email@example.com" className="email" required />
                    </div>
                    <p>Құпия сөз</p>
                    <div className="input-box">
                        <MdLockOutline className="icon" />
                        <input type="password" placeholder="••••••••" required />
                    </div>

                    <div className="remember-forgot">
                        <Link to="#" className="">Құпия сөзді ұмыттыңыз ба?</Link>
                    </div>

                    <button type="submit">Кіру</button>
                </div>
                <div className="register-link">
                    <p>Аккаунт жок па? <Link to="/register" className="reg">Тіркелу</Link></p>
                </div>
            </form>
        </div>
    );
};

export default LoginForm;