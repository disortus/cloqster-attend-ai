import Navbar from "./components/Navbar/Navbar";
import LoginForm from "./components/LoginForm/LoginForm";
import { Route, Routes, Navigate } from "react-router-dom";
import AdminPanel from "./components/AdminPanel/AdminPanel";
import HowItWorks from "./components/HowItsWork/HowItWorks";
import Home from "./components/Home/Home";
import Otmetka from "./components/otmetka/otmetka";


function App() {
    return (
        <>
            <Navbar />

            <div className="container">
                <Routes>
                    {/* Главная страница */}
                    <Route path="/Home" element={<Home />} />

                    <Route path="/mark" element={<Otmetka />} />

                    {/* Логин / регистрация */}
                    <Route path="/login" element={<LoginForm />} />
                

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