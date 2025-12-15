import { createContext, useEffect, useState } from "react";

export const AuthContext = createContext(null);

const API = "http://localhost:5000";

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loadingAuth, setLoadingAuth] = useState(true);

    // восстановление сессии при обновлении страницы
    useEffect(() => {
        (async () => {
            try {
                const res = await fetch(`${API}/me`, {
                    credentials: "include",
                });

                if (res.ok) {
                    const data = await res.json();
                    setUser(data.user ?? data); // поддержка обоих форматов
                } else {
                    setUser(null);
                }
            } catch {
                setUser(null);
            } finally {
                setLoadingAuth(false);
            }
        })();
    }, []);

    const login = (userData) => setUser(userData);

    const logout = async () => {
        try {
            await fetch(`${API}/logout`, {
                method: "POST",
                credentials: "include",
            });
        } finally {
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loadingAuth }}>
            {children}
        </AuthContext.Provider>
    );
}
