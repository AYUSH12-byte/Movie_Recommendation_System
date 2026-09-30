import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

function Navbar() {
  const {
    user,
    isAuthenticated,
    logout,
  } = useAuth();

  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header className="fixed left-0 right-0 top-0 z-50 border-b border-white/5 bg-slate-950/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

        {/* LOGO */}

        <Link
          to="/"
          className="text-2xl font-black tracking-tight"
        >
          Movie
          <span className="text-blue-500">
            AI
          </span>
        </Link>

        {/* DESKTOP NAVIGATION */}

        <nav className="hidden items-center gap-8 md:flex">
          <Link
            to="/"
            className="text-sm font-medium text-slate-300 transition hover:text-white"
          >
            Home
          </Link>

          <Link
            to="/recommendations"
            className="text-sm font-medium text-slate-300 transition hover:text-white"
          >
            Recommendations
          </Link>
        </nav>

        {/* AUTH AREA */}

        {isAuthenticated ? (
          <div className="flex items-center gap-3">

            {/* USER PROFILE */}

            <div className="hidden items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/70 px-3 py-2 sm:flex">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
                {getInitials(user?.name)}
              </div>

              <div className="max-w-[150px]">
                <p className="truncate text-sm font-semibold text-white">
                  {user?.name || "User"}
                </p>

                <p className="truncate text-xs text-slate-500">
                  {user?.email || ""}
                </p>
              </div>
            </div>

            {/* MOBILE USER INITIAL */}

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white sm:hidden">
              {getInitials(user?.name)}
            </div>

            {/* LOGOUT */}

            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-red-500/50 hover:text-red-400"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-blue-500 hover:text-white"
            >
              Login
            </Link>

            <Link
              to="/register"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500"
            >
              Sign Up
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}

/* USER INITIALS */

function getInitials(name) {
  if (!name) {
    return "U";
  }

  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map(
      (part) =>
        part.charAt(0).toUpperCase()
    )
    .join("");
}

export default Navbar;