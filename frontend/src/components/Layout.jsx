import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";
import { DICTIONARIES, useLang } from "../i18n/index.jsx";
import { Button } from "./ui.jsx";

function LangSwitcher() {
  const { lang, setLang, languages } = useLang();
  return (
    <select
      value={lang}
      onChange={(e) => setLang(e.target.value)}
      className="rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-sm"
      aria-label="Language"
    >
      {languages.map((code) => (
        <option key={code} value={code}>
          {DICTIONARIES[code].langName}
        </option>
      ))}
    </select>
  );
}

function Header() {
  const { t } = useLang();
  const { user, isTeacher, logout } = useAuth();
  const navigate = useNavigate();

  const linkClass = ({ isActive }) =>
    `text-sm font-medium transition ${
      isActive ? "text-brand-600" : "text-slate-600 hover:text-brand-600"
    }`;

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4">
        <Link to="/" className="text-lg font-bold text-brand-600">
          CourseSite
        </Link>

        <nav className="flex items-center gap-5">
          <NavLink to="/catalog" className={linkClass}>
            {t("nav.catalog")}
          </NavLink>
          {user && (
            <>
              <NavLink to="/my-courses" className={linkClass}>
                {t("nav.myCourses")}
              </NavLink>
              <NavLink to="/certificates" className={linkClass}>
                {t("nav.certificates")}
              </NavLink>
            </>
          )}
          {isTeacher && (
            <NavLink to="/teach" className={linkClass}>
              {t("nav.teach")}
            </NavLink>
          )}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          <LangSwitcher />
          {user ? (
            <>
              <Link
                to="/profile"
                className="flex items-center gap-2 text-sm text-slate-600 hover:text-brand-600"
                title={t("nav.profile")}
              >
                {user.image ? (
                  <img src={user.image} alt="" className="h-8 w-8 rounded-full object-cover" />
                ) : (
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                    {user.username.slice(0, 1).toUpperCase()}
                  </span>
                )}
                <span className="hidden sm:inline">{user.username}</span>
              </Link>
              <Button
                variant="ghost"
                onClick={async () => {
                  await logout();
                  navigate("/");
                }}
              >
                {t("nav.logout")}
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost">{t("nav.login")}</Button>
              </Link>
              <Link to="/register">
                <Button>{t("nav.register")}</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-slate-200 py-8 text-center text-sm text-slate-500">
        CourseSite. Учебный проект на Django REST Framework и React.
      </footer>
    </div>
  );
}
