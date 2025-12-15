import Navbar from "./components/Navbar/Navbar";
import LoginForm from "./components/LoginForm/LoginForm";
import RegisterForm from "./components/RegisterForm/RegisterForm";
import { Route, Routes, Navigate } from "react-router-dom";

function App() {
    return (
        <>
            <Navbar />

            <div className="container">
                <Routes>
                    {/* Главная страница */}
                    <Route path="/" element={<Home />} />

                    {/* Логин / регистрация */}
                    <Route path="/login" element={<LoginForm />} />
                    <Route path="/register" element={<RegisterForm />} />

                    {/* Если пользователь перейдёт на /home — редирект на / */}
                    <Route path="/home" element={<Navigate to="/" replace />} />

                    <Route path="/admin" element={<div>Admin panel</div>} />

                    {/* На любые неизвестные роуты */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </div>
        </>
    );
}

export default App;

/* ВРЕМЕННАЯ главная страница */
function Home() {
    return (
        <div style={{ padding: "40px", textAlign: "center" }}>
            <h1>Добро пожаловать в CloqsterAI</h1>
            <p>Вы успешно вошли в аккаунт</p>
        </div>
    );
}
