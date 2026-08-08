import { NavLink } from "react-router-dom";

function LogoMark() {
  return (
    <svg width="30" height="30" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="1" width="38" height="38" rx="11" fill="#E8A33D" />
      <rect x="11" y="8" width="14" height="19" rx="2.5" fill="#14192B" />
      <rect x="14" y="12.5" width="8" height="1.6" rx="0.8" fill="#E8A33D" />
      <rect x="14" y="16" width="8" height="1.6" rx="0.8" fill="#E8A33D" />
      <rect x="14" y="19.5" width="5" height="1.6" rx="0.8" fill="#E8A33D" />
      <circle cx="24.5" cy="24.5" r="6" fill="#FAF7F1" stroke="#14192B" strokeWidth="2.4" />
      <line x1="29" y1="29" x2="33.5" y2="33.5" stroke="#14192B" strokeWidth="2.6" strokeLinecap="round" />
      <path d="M22 24.3l1.6 1.6 3-3.2" stroke="#14192B" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <LogoMark />
        <span className="navbar-mark">Resume Screener</span>
      </div>
      <div className="navbar-links">
        <NavLink to="/" end className={({ isActive }) => `navbar-link ${isActive ? "active" : ""}`}>
          💬 Chat
        </NavLink>
        <NavLink to="/vector-db" className={({ isActive }) => `navbar-link ${isActive ? "active" : ""}`}>
          🗂 Vector DB
        </NavLink>
      </div>
    </nav>
  );
}
