import { useState, useRef, useEffect } from "react";

function Dropdown() {
    const [open, setOpen] = useState(false);
    const [language, setLanguage] = useState("Қазақша"); // язык по умолчанию
    const ref = useRef(null);

    const toggle = () => setOpen(!open);

    const choose = (lang) => {
        setLanguage(lang);
        setOpen(false);
    };

    useEffect(() => {
        const handleClick = (e) => {
            if (ref.current && !ref.current.contains(e.target)) {
                setOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, []);

    return (
        <div className="lang-dropdown" ref={ref}>
            <button className="lang-btn" onClick={toggle}>
                {language} ▾
            </button>

            {open && (
                <div className="lang-menu">
                    <div className="lang-item" onClick={() => choose("Қазақша")}>
                        Қазақша
                    </div>
                    <div className="lang-item" onClick={() => choose("Русский")}>
                        Русский
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dropdown;