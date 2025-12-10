import React from "react"

function Dropdown() {
    return (
        <header className="dropdown">
           <button className="menu-button"></button>
            <nav className="menu">
                <ul className="menu-list">
                    <li className="menu-item">Орыс тілі</li>
                    <li className="menu-item">Қазақ тілі</li>
                </ul>
            </nav>
        </header>
    )
}