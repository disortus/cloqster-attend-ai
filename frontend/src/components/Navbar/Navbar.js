import { Link, useNavigate } from "react-router-dom";
import { useContext, useEffect, useRef, useState } from "react";
import Dropdown from "./Dropdown";
import { AuthContext } from "../../auth/AuthContext";

function Navbar() {
    const { user, logout, loadingAuth } = useContext(AuthContext);
    const [open, setOpen] = useState(false);
    const menuRef = useRef(null);
    const navigate = useNavigate();

    const avatarUrl = user?.fullname
        ? `https://api.dicebear.com/9.x/initials/svg?seed=${encodeURIComponent(user.fullname)}`
        : `https://api.dicebear.com/9.x/initials/svg?seed=User`;

    // закрывать меню при клике вне него
    useEffect(() => {
        const onDocClick = (e) => {
            if (!menuRef.current) return;
            if (!menuRef.current.contains(e.target)) setOpen(false);
        };
        document.addEventListener("mousedown", onDocClick);
        return () => document.removeEventListener("mousedown", onDocClick);
    }, []);

    const handleLogout = async () => {
        setOpen(false);
        await logout();
        navigate("/login");
    };

    const goAdmin = () => {
        setOpen(false);
        navigate("/admin"); // сделай роут /admin в App.js
    };

    return (
        <nav className="nav">
            <Link to="/home" className="site-title">CloqsterAI</Link>

            <ul>
                <li><Link to="/how-it-works" className="top">Қалай жұмыс істейді</Link></li>
                <li><Link to="/functions" className="top">Мүмкіндіктер</Link></li>
                <li><Link to="/Mark" className="top">Белгі қою</Link></li>
                <li><Link to="/history" className="top">Тарих</Link></li>
            </ul>

            <ul>
                <li><Dropdown /></li>

                <li ref={menuRef} style={{ position: "relative" }}>
                    {loadingAuth ? null : user ? (
                        <>
                            <button
                                onClick={() => setOpen((v) => !v)}
                                style={{ background: "transparent", border: "none", padding: 0, cursor: "pointer" }}
                                aria-label="User menu"
                            >
                                <img
                                    src={avatarUrl}
                                    alt="avatar"
                                    style={{ width: 36, height: 36, borderRadius: "50%" }}
                                />
                            </button>

                            {open && (
                                <div
                                    style={{
                                        position: "absolute",
                                        right: 0,
                                        top: "calc(100% + 10px)",
                                        minWidth: 180,
                                        background: "white",
                                        border: "1px solid rgba(0,0,0,0.12)",
                                        borderRadius: 10,
                                        boxShadow: "0 10px 24px rgba(0,0,0,0.12)",
                                        padding: 8,
                                        zIndex: 9999,
                                    }}
                                >
                                    <div style={{ padding: "8px 10px", fontSize: 14, opacity: 0.8 }}>
                                        {user.fullname || user.email}
                                    </div>

                                    {/* Админ-панель показываем только если роль admin */}
                                    {user.role === "admin" && (
                                        <button
                                            onClick={goAdmin}
                                            style={{
                                                width: "100%",
                                                textAlign: "left",
                                                padding: "10px",
                                                border: "none",
                                                background: "transparent",
                                                cursor: "pointer",
                                                borderRadius: 8,
                                            }}
                                            onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(0,0,0,0.06)")}
                                            onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                                        >
                                            Админ панель
                                        </button>
                                    )}

                                    <button
                                        onClick={handleLogout}
                                        style={{
                                            width: "100%",
                                            textAlign: "left",
                                            padding: "10px",
                                            border: "none",
                                            background: "transparent",
                                            cursor: "pointer",
                                            borderRadius: 8,
                                        }}
                                        onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(0,0,0,0.06)")}
                                        onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                                    >
                                        Выход
                                    </button>
                                </div>
                            )}
                        </>
                    ) : (
                        <Link to="/login" className="login">Кіру</Link>
                    )}
                </li>
            </ul>
        </nav>
    );
}

export default Navbar;
