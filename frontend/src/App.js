import Navbar from "./components/Navbar/Navbar";
import LoginForm from "./components/LoginForm/LoginForm";
import RegisterForm from "./components/RegisterForm/RegisterForm";
import { Route, Routes, Navigate } from "react-router-dom";
import AdminPanel from "./components/AdminPanel/AdminPanel";
import HowItWorks from "./components/HowItsWork/HowItWorks";
import Home from "./components/Home/Home";
import StudentPanel from './components/StudentPanel/StudentPanel';

function App() {
    return (
        <>
            <Navbar />

            <div className="container">
                <Routes>
                    {/* Главная страница */}
                    <Route path="/Home" element={<Home />} />

                    <Route path="/student" element={<StudentPanel />} />
                    <Route path="/mark" element={<StudentPanel />} /> 

                    {/* Логин / регистрация */}
                    <Route path="/login" element={<LoginForm />} />
                    <Route path="/register" element={<RegisterForm />} />

                    {/* Как это работает ) */}
                    <Route path="/how-it-workS" element={<HowItWorks />} />

                    {/* Если пользователь перейдёт на /home — редирект на / */}
                    <Route path="/home" element={<Navigate to="/" replace />} />

                    <Route path="/admin" element={<AdminPanel />} />


                    {/* На любые неизвестные роуты */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </div>
        </>
    );
}

export default App; 