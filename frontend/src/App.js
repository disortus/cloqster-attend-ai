import Navbar from "./components/Navbar/Navbar";
import LoginForm from "./components/LoginForm/LoginForm";
import { Route, Routes, Navigate } from "react-router-dom";
import AdminPanel from "./components/AdminPanel/AdminPanel";
import CuratorPanel from "./components/CuratorPanel/CuratorPanel";
import TeacherPanel from "./components/TeacherPanel/TeacherPanel";
import StudentPanel from "./components/StudentPanel/StudentPanel";
import HowItWorks from "./components/HowItsWork/HowItWorks";
import Home from "./components/Home/Home";
import Otmetka from "./components/otmetka/otmetka";
import AttendanceHistory from './components/AttendanceHistory/AttendanceHistory';
import Features from './components/Features/Features';


function App() {
    return (
        <>
            <Navbar />

            <div className="container">
                <Routes>
                    {/* Главная страница */}
                    <Route path="/Home" element={<Home />} />

                    <Route path="/features" element={<Features />} />

                    <Route path="/mark" element={<Otmetka />} />

                    <Route path="/history" element={<AttendanceHistory />} />

                    {/* Логин / регистрация */}
                    <Route path="/login" element={<LoginForm />} />
                

                    {/* Как это работает ) */}
                    <Route path="/how-it-workS" element={<HowItWorks />} />

                    {/* Если пользователь перейдёт на /home — редирект на / */}
                    <Route path="/home" element={<Navigate to="/" replace />} />

                    <Route path="/admin" element={<AdminPanel />} />

                    <Route path="/curator" element={<CuratorPanel />} />

                    <Route path="/teacher" element={<TeacherPanel />} />

                    <Route path="/student" element={<StudentPanel />} />

                    {/* На любые неизвестные роуты */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </div>
        </>
    );
}

export default App; 