import {Link} from "react-router-dom";
import Dropdown from "./Dropdown"

function Navbar() {
    return <nav className="nav">
        <Link to="/home" className="site-title">CloqsterAI</Link>
        <ul>
            <li>
                <Link to="/how-it-works" className="top">Қалай жұмыс істейді</Link>
            </li>
            <li>
                <Link to="/functions" className="top">Мүмкіндіктер</Link>
            </li>
            <li>
                <Link to="/Mark" className="top">Белгі қою</Link>
            </li>
            <li>
                <Link to="/history" className="top">Тарих</Link>
            </li>
        </ul>
        <ul>
            <li>
                {/*<Dropdown />*/}
            </li>
            <li>
                <Link to="/login" className="login">Кіру</Link>
            </li>
            <li>
                <Link to="/register" className="register">Тіркелу</Link>
            </li>
        </ul>
    </nav>
}

export default Navbar